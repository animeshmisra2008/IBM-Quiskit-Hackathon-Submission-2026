"""Main challenge: connect SLC-selected errors to PNA and noisy simulation.

Noise rates are synthetic calibration inputs for a reproducible local run.
The same rates generate the simulated noise and PNA correction model. A
hardware study would replace these with calibration results from a backend.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.primitives import BackendEstimatorV2
from qiskit.quantum_info import (
    DensityMatrix,
    Operator,
    Pauli,
    PauliLindbladMap,
    QubitSparsePauliList,
    SparsePauliOp,
    Statevector,
)
from qiskit_aer import AerSimulator
from qiskit_aer.noise.errors import PauliLindbladError
from qiskit_addon_pna import generate_noise_mitigating_observable
from qiskit_addon_slc.bounds import (
    compute_backward_bounds,
    compute_forward_bounds,
    compute_local_scales,
    merge_bounds,
)
from qiskit_addon_slc.utils import generate_noise_model_paulis
from samplomatic.annotations import InjectNoise
from samplomatic.transpiler import generate_boxing_pass_manager
from samplomatic.utils import find_unique_box_instructions, get_annotation


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
NOISE_SCALES = (0.5, 1.0, 2.0)
BIAS_TOLERANCE = 0.05
ESTIMATOR_PRECISION = 0.01
THETA = Parameter("theta")


def make_circuit() -> QuantumCircuit:
    circuit = QuantumCircuit(5)
    for qubit in range(5):
        circuit.h(qubit)
        circuit.rx(THETA, qubit)
    for _ in range(2):
        for start in (0, 1):
            for qubit in range(start, 4, 2):
                circuit.cz(qubit, qubit + 1)
        for qubit in range(5):
            circuit.rx(THETA / 2, qubit)
    return circuit


def make_model(paulis: QubitSparsePauliList, scale: float) -> PauliLindbladMap:
    rng = np.random.default_rng(20261031)
    rates = (0.002 + rng.random(len(paulis)) * 0.001) * scale
    return PauliLindbladMap.from_components(
        rates,
        QubitSparsePauliList.from_sparse_list(
            paulis.to_sparse_list(), paulis.num_qubits
        ),
    )


def align_learned_model(
    learned: PauliLindbladMap | None,
    target_paulis: QubitSparsePauliList,
    scale: float,
) -> PauliLindbladMap:
    """Align learned rates to SLC's candidate order, using zero for absent terms."""
    learned_rates = {
        (pauli, tuple(qubits)): rate
        for pauli, qubits, rate in learned.to_sparse_list()
    } if learned is not None else {}
    terms = target_paulis.to_sparse_list()
    rates = [learned_rates.get((pauli, tuple(qubits)), 0.0) * scale for pauli, qubits in terms]
    return PauliLindbladMap.from_components(
        rates,
        QubitSparsePauliList.from_sparse_list(terms, target_paulis.num_qubits),
    )


def learn_with_noise_learner_v3(
    backend,
    boxed_circuit: QuantumCircuit,
) -> dict[str, PauliLindbladMap]:
    """Optional hardware-backed calibration path; submits an IBM Quantum job."""
    from qiskit_ibm_runtime import NoiseLearnerV3, NoiseLearnerV3Options

    unique_layers = find_unique_box_instructions(
        boxed_circuit, normalize_annotations=None, undress_boxes=True
    )
    results = NoiseLearnerV3(backend, NoiseLearnerV3Options()).run(unique_layers).result()
    learned_models = {}
    for instruction, learned_result in zip(unique_layers, results, strict=False):
        annotation = get_annotation(instruction.operation, InjectNoise)
        if annotation is not None:
            learned_models[annotation.ref] = learned_result.to_pauli_lindblad_map()
    return learned_models


def pauli_from_sparse(pauli_string: str, qubits: list[int], width: int) -> Pauli:
    label = ["I"] * width
    for char, qubit in zip(pauli_string, qubits, strict=True):
        label[width - qubit - 1] = char
    return Pauli("".join(label))


def aer_error(model: PauliLindbladMap) -> PauliLindbladError:
    sparse_terms = model.to_sparse_list()
    generators = [
        pauli_from_sparse(pauli, qubits, model.num_qubits)
        for pauli, qubits, _rate in sparse_terms
    ]
    rates = [rate for _pauli, _qubits, rate in sparse_terms]
    return PauliLindbladError(generators, rates)


def simulate_with_learned_noise(
    boxed: QuantumCircuit,
    models: dict[str, PauliLindbladMap],
    backend: AerSimulator,
) -> tuple[QuantumCircuit, DensityMatrix]:
    """Unbox the circuit and insert the exact Pauli-Lindblad channel per layer."""
    noisy = QuantumCircuit(boxed.num_qubits)
    for instruction in boxed.data:
        body = instruction.operation.body
        local_to_global = dict(zip(body.qubits, instruction.qubits, strict=True))
        for body_instruction in body.data:
            noisy.append(
                body_instruction.operation,
                [local_to_global[q] for q in body_instruction.qubits],
            )
        annotation = get_annotation(instruction.operation, InjectNoise)
        if annotation is not None:
            error = aer_error(models[annotation.ref])
            noisy.append(error.to_instruction(), list(instruction.qubits))

    density_circuit = noisy.copy()
    density_circuit.save_density_matrix()
    density = DensityMatrix(backend.run(density_circuit).result().data(0)["density_matrix"])
    return noisy, density


def slc_mask_for_references(
    boxed: QuantumCircuit,
    scales: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    """Keep an error term if SLC retained it at any occurrence of that layer."""
    masks: dict[str, np.ndarray] = {}
    for instruction in boxed.data:
        annotation = get_annotation(instruction.operation, InjectNoise)
        if annotation is None:
            continue
        current = np.asarray(scales[annotation.modifier_ref]) != 0
        if annotation.ref in masks:
            masks[annotation.ref] |= current
        else:
            masks[annotation.ref] = current.copy()
    return masks


def keep_model_terms(
    model: PauliLindbladMap,
    paulis: QubitSparsePauliList,
    keep: np.ndarray,
) -> PauliLindbladMap:
    rates = np.asarray(model.rates).copy()
    rates[~keep] = 0.0
    return PauliLindbladMap.from_components(
        rates,
        QubitSparsePauliList.from_sparse_list(
            paulis.to_sparse_list(), paulis.num_qubits
        ),
    )


def run_workflow(
    parameterized_circuit: QuantumCircuit,
    parameter_values: dict[Parameter, float],
    backend: AerSimulator,
    calibration_models: dict[str, PauliLindbladMap] | None = None,
) -> dict:
    """Run the local workflow for a parameterized circuit and Aer backend."""
    circuit = parameterized_circuit.assign_parameters(parameter_values)
    observable = Pauli("IIXII")  # X on the center qubit
    ideal_state = Statevector.from_instruction(circuit)
    ideal_value = float(np.real(ideal_state.expectation_value(observable)))
    fidelity_projector = SparsePauliOp.from_operator(
        Operator(np.outer(ideal_state.data, ideal_state.data.conj()))
    ).simplify(atol=1e-10)
    estimator = BackendEstimatorV2(
        backend=backend,
        options={"seed_simulator": 20261031, "default_precision": ESTIMATOR_PRECISION},
    )
    boxing = generate_boxing_pass_manager(
        inject_noise_targets="all",
        inject_noise_strategy="individual_modification",
        inject_noise_site="after",
        twirling_strategy="active",
        remove_barriers="never",
    )
    boxed = boxing.run(circuit)
    noise_paulis = generate_noise_model_paulis(find_unique_box_instructions(boxed))
    forward = compute_forward_bounds(boxed, noise_paulis, observable)
    backward = compute_backward_bounds(boxed, noise_paulis)
    result_rows = []

    for noise_scale in NOISE_SCALES:
        if calibration_models is None:
            full_models = {
                ref: make_model(paulis, noise_scale)
                for ref, paulis in noise_paulis.items()
            }
        else:
            full_models = {
                # Missing learned layers keep the candidate shape and get zero rates.
                ref: align_learned_model(calibration_models.get(ref), paulis, noise_scale)
                for ref, paulis in noise_paulis.items()
            }
        merged = merge_bounds(boxed, forward, backward, full_models)
        _full_scales, full_cost, full_bias = compute_local_scales(
            boxed, merged, full_models, bias_tolerance=0.0
        )
        slc_scales, slc_cost, slc_bias = compute_local_scales(
            boxed, merged, full_models, bias_tolerance=BIAS_TOLERANCE
        )
        masks = slc_mask_for_references(boxed, slc_scales)
        slc_models = {
            ref: keep_model_terms(model, noise_paulis[ref], masks[ref])
            for ref, model in full_models.items()
        }

        pna_results = {}
        for label, models in (("pna_full", full_models), ("slc_plus_pna", slc_models)):
            started = time.perf_counter()
            mitigated_observable = generate_noise_mitigating_observable(
                boxed,
                observable,
                models,
                max_err_terms=1000,
                max_obs_terms=1000,
                num_processes=1,
                inject_noise_before=False,
            )
            pna_seconds = time.perf_counter() - started
            pna_results[label] = (mitigated_observable, pna_seconds)

        fidelity_started = time.perf_counter()
        mitigated_projector = generate_noise_mitigating_observable(
            boxed,
            fidelity_projector,
            full_models,
            max_err_terms=10000,
            max_obs_terms=10000,
            num_processes=1,
            search_step=8,
            inject_noise_before=False,
        )
        fidelity_pna_seconds = time.perf_counter() - fidelity_started

        slc_fidelity_started = time.perf_counter()
        mitigated_projector_slc = generate_noise_mitigating_observable(
            boxed,
            fidelity_projector,
            slc_models,
            max_err_terms=10000,
            max_obs_terms=10000,
            num_processes=1,
            search_step=8,
            inject_noise_before=False,
        )
        slc_fidelity_pna_seconds = time.perf_counter() - slc_fidelity_started

        simulation_started = time.perf_counter()
        noisy_circuit, noisy_state = simulate_with_learned_noise(boxed, full_models, backend)
        simulation_seconds = time.perf_counter() - simulation_started
        noisy_value = float(np.real(noisy_state.expectation_value(observable)))
        primitive_noisy = float(
            np.asarray(estimator.run([(noisy_circuit, observable)], precision=ESTIMATOR_PRECISION)
                       .result()[0].data.evs).item()
        )
        primitive_full = float(
            np.asarray(estimator.run(
                [(noisy_circuit, pna_results["pna_full"][0])], precision=ESTIMATOR_PRECISION
            ).result()[0].data.evs).item()
        )
        primitive_slc = float(
            np.asarray(estimator.run(
                [(noisy_circuit, pna_results["slc_plus_pna"][0])], precision=ESTIMATOR_PRECISION
            ).result()[0].data.evs).item()
        )
        state_fidelity = float(
            np.real(noisy_state.expectation_value(ideal_state.to_operator()))
        )
        pna_state_fidelity = float(np.real(noisy_state.expectation_value(mitigated_projector)))
        slc_pna_state_fidelity = float(
            np.real(noisy_state.expectation_value(mitigated_projector_slc))
        )

        row = {
            "noise_scale": noise_scale,
            "ideal_expectation": ideal_value,
            "noisy_expectation": primitive_noisy,
            "exact_noisy_expectation": noisy_value,
            "full_pna_expectation": primitive_full,
            "exact_full_pna_expectation": float(
                np.real(noisy_state.expectation_value(pna_results["pna_full"][0]))
            ),
            "slc_plus_pna_expectation": primitive_slc,
            "exact_slc_plus_pna_expectation": float(
                np.real(noisy_state.expectation_value(pna_results["slc_plus_pna"][0]))
            ),
            "noisy_state_fidelity": state_fidelity,
            "full_pna_state_fidelity_estimate": pna_state_fidelity,
            "slc_plus_pna_state_fidelity_estimate": slc_pna_state_fidelity,
            "fidelity_projector_pauli_terms": len(fidelity_projector),
            "pna_fidelity_preprocessing_seconds": fidelity_pna_seconds,
            "slc_pna_fidelity_preprocessing_seconds": slc_fidelity_pna_seconds,
            "full_pna_expectation_error": abs(
                ideal_value
                - float(np.real(noisy_state.expectation_value(pna_results["pna_full"][0])))
            ),
            "slc_plus_pna_expectation_error": abs(
                ideal_value
                - float(np.real(noisy_state.expectation_value(pna_results["slc_plus_pna"][0])))
            ),
            "slc_sampling_cost": slc_cost,
            "slc_bias_bound": slc_bias,
            "full_sampling_cost": full_cost,
            "full_bias_bound": full_bias,
            "full_model_term_count": sum(len(model.rates) for model in full_models.values()),
            "slc_model_term_count": sum(
                int(np.count_nonzero(model.rates)) for model in slc_models.values()
            ),
            "full_pna_observable_terms": len(pna_results["pna_full"][0]),
            "slc_pna_observable_terms": len(pna_results["slc_plus_pna"][0]),
            "full_pna_preprocessing_seconds": pna_results["pna_full"][1],
            "slc_pna_preprocessing_seconds": pna_results["slc_plus_pna"][1],
            "noisy_simulation_seconds": simulation_seconds,
            "estimator_precision": ESTIMATOR_PRECISION,
        }
        result_rows.append(row)

    return {
        "method": "SLC-selected PNA on a local Pauli-Lindblad noisy simulator",
        "noise_source": (
            "synthetic local rates; not an IBM hardware measurement"
            if calibration_models is None
            else "NoiseLearnerV3 calibration rates supplied by caller"
        ),
        "calibration_note": (
            "Synthetic rates are for reproducible local simulation."
            if calibration_models is None
            else "Calibration models were supplied by the caller; verify their provenance before reporting hardware results."
        ),
        "note": "BackendEstimatorV2 estimates the selected X observable. Full PNA and SLC + PNA also correct the ideal-state fidelity projector; exact noisy-state fidelity is computed separately.",
        "qubits": circuit.num_qubits,
        "cz_gates": sum(inst.operation.name == "cz" for inst in circuit.data),
        "observable": "X on center qubit",
        "parameter_values": {str(key): value for key, value in parameter_values.items()},
        "slc_bias_tolerance": BIAS_TOLERANCE,
        "results": result_rows,
    }


def main() -> None:
    parameterized_circuit = make_circuit()
    backend = AerSimulator(method="density_matrix")
    output = run_workflow(
        parameterized_circuit,
        {THETA: 0.28},
        backend,
    )
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "phase3_noise_sweep.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
