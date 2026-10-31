import numpy as np
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector

from qiskit_aer import AerSimulator
from qiskit_aer.noise import (
    NoiseModel,
    depolarizing_error,
    ReadoutError
)


# ==========================================
# 1. CREATE CLIFFORD-ONLY CIRCUIT
# ==========================================

clifford = QuantumCircuit(3)

clifford.h(0)
clifford.h(1)
clifford.h(2)

clifford.cx(0, 1)
clifford.cx(1, 2)

clifford.s(0)
clifford.h(1)


# ==========================================
# 2. CREATE T-DOPED CIRCUIT
# ==========================================

t_doped = QuantumCircuit(3)

t_doped.h(0)
t_doped.h(1)
t_doped.h(2)

t_doped.cx(0, 1)
t_doped.cx(1, 2)

# Introduce multiple T gates
t_doped.t(0)
t_doped.t(1)
t_doped.t(2)

t_doped.cx(0, 1)

t_doped.t(0)
t_doped.t(1)

t_doped.s(0)
t_doped.h(1)


# ==========================================
# 3. CALCULATE IDEAL PROBABILITIES
# ==========================================

ideal_clifford = Statevector.from_instruction(
    clifford
).probabilities_dict()

ideal_t = Statevector.from_instruction(
    t_doped
).probabilities_dict()


# ==========================================
# 4. CREATE NOISE MODEL
# ==========================================

noise = NoiseModel()

noise.add_all_qubit_quantum_error(
    depolarizing_error(0.01, 2),
    ["cx"]
)

noise.add_all_qubit_readout_error(
    ReadoutError([
        [0.99, 0.01],
        [0.01, 0.99]
    ])
)


# Density-matrix simulation supports T gates
# and noisy quantum circuits.

simulator = AerSimulator(
    method="density_matrix",
    noise_model=noise
)


# ==========================================
# 5. FUNCTION TO RUN EXPERIMENT
# ==========================================

def run_experiment(circuit, ideal_probs):

    measured = circuit.copy()
    measured.measure_all()

    compiled = transpile(
        measured,
        simulator,
        optimization_level=0
    )

    result = simulator.run(
        compiled,
        shots=10000,
        seed_simulator=42
    ).result()

    counts = result.get_counts()

    total = sum(counts.values())

    observed = {
        key: value / total
        for key, value in counts.items()
    }

    keys = set(ideal_probs) | set(observed)

    fidelity = sum(
        np.sqrt(
            ideal_probs.get(key, 0) *
            observed.get(key, 0)
        )
        for key in keys
    ) ** 2

    return counts, fidelity


# ==========================================
# 6. RUN BOTH EXPERIMENTS
# ==========================================

clifford_counts, clifford_fidelity = run_experiment(
    clifford,
    ideal_clifford
)

t_counts, t_fidelity = run_experiment(
    t_doped,
    ideal_t
)


# ==========================================
# 7. DISPLAY RESULTS
# ==========================================

print("\n================================")
print("CLIFFORD VS T-DOPED EXPERIMENT")
print("================================")

print("\nClifford-only fidelity:")
print(round(clifford_fidelity, 5))

print("\nT-doped fidelity:")
print(round(t_fidelity, 5))

print("\nClifford circuit counts:")
print(clifford_counts)

print("\nT-doped circuit counts:")
print(t_counts)


# ==========================================
# 8. CREATE COMPARISON GRAPH
# ==========================================

plt.figure(figsize=(8, 5))

plt.bar(
    ["Clifford-only", "T-doped"],
    [clifford_fidelity, t_fidelity]
)

plt.ylabel("Measurement Distribution Fidelity")
plt.title("Clifford vs T-Doped Circuit")

plt.ylim(0, 1)

plt.savefig("t_gate_comparison.png")

plt.show()


print("\nGraph saved as t_gate_comparison.png")