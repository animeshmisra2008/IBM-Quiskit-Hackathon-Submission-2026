"""Phase 1: compare one ideal circuit with a noisy simulation.

This is a small baseline for the Track 2 mitigation workflow. It measures the
average Z value of the middle qubit in a three-qubit CZ chain.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SHOTS = 20_000
SEED = 20261031


def make_circuit(theta: float = 0.42) -> QuantumCircuit:
    """Prepare a small, parameterized state and entangle neighboring qubits."""
    circuit = QuantumCircuit(3, 3)
    for qubit in range(3):
        circuit.h(qubit)
        circuit.ry(theta, qubit)
    circuit.cz(0, 1)
    circuit.cz(1, 2)
    circuit.ry(theta / 2, 1)
    circuit.measure(range(3), range(3))
    return circuit


def middle_qubit_z(counts: dict[str, int]) -> float:
    """Estimate <Z> for qubit 1; Qiskit prints bitstrings as q2 q1 q0."""
    total = sum(counts.values())
    average = sum((1 if key.replace(" ", "")[-2] == "0" else -1) * count
                  for key, count in counts.items())
    return average / total


def run_once(noisy: bool) -> tuple[float, float]:
    circuit = make_circuit()
    noise_model = None
    if noisy:
        noise_model = NoiseModel()
        noise_model.add_all_qubit_quantum_error(
            depolarizing_error(0.03, 2), ["cz"]
        )
    simulator = AerSimulator(noise_model=noise_model, seed_simulator=SEED)
    start = time.perf_counter()
    counts = simulator.run(circuit, shots=SHOTS).result().get_counts()
    elapsed = time.perf_counter() - start
    return middle_qubit_z(counts), elapsed


def main() -> None:
    ideal_value, ideal_seconds = run_once(noisy=False)
    noisy_value, noisy_seconds = run_once(noisy=True)
    result = {
        "qubits": 3,
        "shots": SHOTS,
        "cz_depolarizing_error_probability": 0.03,
        "observable": "Z on middle qubit",
        "ideal_expectation": ideal_value,
        "noisy_expectation": noisy_value,
        "absolute_change": abs(noisy_value - ideal_value),
        "ideal_runtime_seconds": ideal_seconds,
        "noisy_runtime_seconds": noisy_seconds,
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "phase1_baseline.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
