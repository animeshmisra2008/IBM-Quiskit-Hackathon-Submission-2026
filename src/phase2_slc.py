"""Phase 2: use the Qiskit SLC add-on to estimate which errors matter most.

The official NoiseLearnerV3 submits a learning job to IBM Quantum. Because no
IBM account is configured, this local experiment uses explicit synthetic
calibration rates, as in the SLC add-on's quickstart. The rates are clearly
tagged as simulated inputs, not hardware measurements.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import (
    Pauli,
    PauliLindbladMap,
    QubitSparsePauliList,
)
from qiskit_addon_slc.bounds import (
    compute_backward_bounds,
    compute_forward_bounds,
    compute_local_scales,
    merge_bounds,
)
from qiskit_addon_slc.utils import generate_noise_model_paulis
from samplomatic.transpiler import generate_boxing_pass_manager
from samplomatic.utils import find_unique_box_instructions


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def make_circuit() -> QuantumCircuit:
    circuit = QuantumCircuit(5)
    for qubit in range(5):
        circuit.h(qubit)
        circuit.rx(0.28, qubit)
    for _ in range(2):
        for start in (0, 1):
            for qubit in range(start, 4, 2):
                circuit.cz(qubit, qubit + 1)
        for qubit in range(5):
            circuit.rx(0.17, qubit)
    return circuit


def main() -> None:
    circuit = make_circuit()
    observable = Pauli("IIXII")  # X on the center qubit (qubit 2)
    boxing = generate_boxing_pass_manager(
        inject_noise_targets="all",
        inject_noise_strategy="individual_modification",
        inject_noise_site="after",
        twirling_strategy="active",
        remove_barriers="never",
    )
    boxed_circuit = boxing.run(circuit)
    noise_paulis = generate_noise_model_paulis(
        find_unique_box_instructions(boxed_circuit)
    )

    # Synthetic calibration rates create a reproducible local stand-in for a
    # hardware noise-learning result. Values are per Pauli error generator.
    rng = np.random.default_rng(20261031)
    noise_rates = {
        layer_id: PauliLindbladMap.from_components(
            0.002 + rng.random(len(paulis)) * 0.001,
            QubitSparsePauliList.from_sparse_list(
                paulis.to_sparse_list(), paulis.num_qubits
            ),
        )
        for layer_id, paulis in noise_paulis.items()
    }

    start = time.perf_counter()
    forward = compute_forward_bounds(boxed_circuit, noise_paulis, observable)
    backward = compute_backward_bounds(boxed_circuit, noise_paulis)
    merged = merge_bounds(boxed_circuit, forward, backward, noise_rates)
    full_scales, full_cost, full_bias = compute_local_scales(
        boxed_circuit, merged, noise_rates, bias_tolerance=0.0
    )
    slc_scales, slc_cost, slc_bias = compute_local_scales(
        boxed_circuit, merged, noise_rates, bias_tolerance=0.05
    )
    elapsed = time.perf_counter() - start

    all_terms = sum(len(scales) for scales in full_scales.values())
    retained_terms = sum(int(np.count_nonzero(scales)) for scales in slc_scales.values())
    result = {
        "method": "Qiskit Shaded Lightcones (SLC)",
        "calibration_source": "synthetic local rates; not measured by NoiseLearnerV3",
        "circuit_qubits": circuit.num_qubits,
        "cz_gates": sum(inst.operation.name == "cz" for inst in circuit.data),
        "observable": "X on the center qubit",
        "noise_layers": len(noise_paulis),
        "candidate_pauli_error_terms": all_terms,
        "retained_terms_after_shading": retained_terms,
        "full_mitigation_sampling_cost": full_cost,
        "full_mitigation_bias_bound": full_bias,
        "slc_sampling_cost": slc_cost,
        "slc_bias_bound": slc_bias,
        "sampling_cost_reduction_fraction": 1 - slc_cost / full_cost,
        "analysis_runtime_seconds": elapsed,
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "phase2_slc.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
