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
# 1. CLIFFORD-ONLY CIRCUIT
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
# 2. T-DOPED CIRCUIT
# ==========================================

t_doped = QuantumCircuit(3)

t_doped.h(0)
t_doped.h(1)
t_doped.h(2)

t_doped.cx(0, 1)
t_doped.cx(1, 2)

t_doped.t(0)
t_doped.t(1)
t_doped.t(2)

t_doped.cx(0, 1)

t_doped.t(0)
t_doped.t(1)

t_doped.s(0)
t_doped.h(1)


# ==========================================
# 3. IDEAL OUTPUT PROBABILITIES
# ==========================================

ideal_clifford = Statevector.from_instruction(
    clifford
).probabilities_dict()

ideal_t = Statevector.from_instruction(
    t_doped
).probabilities_dict()


# ==========================================
# 4. IMPROVED NOISE MODEL
# ==========================================

noise = NoiseModel()

# Single-qubit gate noise
noise.add_all_qubit_quantum_error(
    depolarizing_error(0.001, 1),
    ["rz", "sx"]
)

# Two-qubit gate noise
noise.add_all_qubit_quantum_error(
    depolarizing_error(0.01, 2),
    ["cx"]
)

# Measurement noise
noise.add_all_qubit_readout_error(
    ReadoutError([
        [0.99, 0.01],
        [0.01, 0.99]
    ])
)


simulator = AerSimulator(
    method="density_matrix",
    noise_model=noise
)


# ==========================================
# 5. FIDELITY CALCULATION
# ==========================================

def calculate_fidelity(ideal, counts):

    total = sum(counts.values())

    observed = {
        key: value / total
        for key, value in counts.items()
    }

    keys = set(ideal) | set(observed)

    fidelity = sum(
        np.sqrt(
            ideal.get(key, 0) *
            observed.get(key, 0)
        )
        for key in keys
    ) ** 2

    return fidelity


# ==========================================
# 6. RUN EXPERIMENT
# ==========================================

def run_experiment(circuit, ideal):

    measured = circuit.copy()
    measured.measure_all()

    compiled = transpile(
        measured,
        simulator,
        optimization_level=0
    )

    print("\nCompiled gate counts:")
    print(compiled.count_ops())

    result = simulator.run(
        compiled,
        shots=10000,
        seed_simulator=42
    ).result()

    counts = result.get_counts()

    fidelity = calculate_fidelity(
        ideal,
        counts
    )

    return fidelity, counts


# ==========================================
# 7. EXECUTE BOTH CIRCUITS
# ==========================================

print("\n===== CLIFFORD EXPERIMENT =====")

clifford_fidelity, clifford_counts = run_experiment(
    clifford,
    ideal_clifford
)


print("\n===== T-DOPED EXPERIMENT =====")

t_fidelity, t_counts = run_experiment(
    t_doped,
    ideal_t
)


# ==========================================
# 8. DISPLAY RESULTS
# ==========================================

print("\n======================================")
print("FAIR CIRCUIT COMPARISON")
print("======================================")

print("Clifford fidelity:", round(clifford_fidelity, 5))

print("T-doped fidelity:", round(t_fidelity, 5))


# ==========================================
# 9. CREATE GRAPH
# ==========================================

plt.figure(figsize=(8, 5))

plt.bar(
    ["Clifford-only", "T-doped"],
    [clifford_fidelity, t_fidelity]
)

plt.ylim(0, 1)

plt.ylabel("Measurement Distribution Fidelity")

plt.title("Clifford vs T-Doped Circuit - Noisy Simulation")

plt.savefig("fair_comparison.png")

plt.show()

print("\nGraph saved as fair_comparison.png")