from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from qiskit_aer.noise import (
    NoiseModel,
    depolarizing_error,
    ReadoutError
)

import numpy as np


SHOTS = 10000


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

# Introduce non-Clifford T gates
t_doped.t(0)
t_doped.t(1)
t_doped.t(2)

t_doped.cx(0, 1)

t_doped.t(0)
t_doped.t(1)

t_doped.s(0)
t_doped.h(1)


# ==========================================
# 3. CALCULATE IDEAL DISTRIBUTIONS
# ==========================================

def get_ideal_distribution(circuit):

    state = Statevector.from_instruction(circuit)

    return state.probabilities_dict()


ideal_clifford = get_ideal_distribution(clifford)
ideal_t = get_ideal_distribution(t_doped)


# ==========================================
# 4. CREATE SAME NOISE MODEL FOR BOTH
# ==========================================

noise_model = NoiseModel()

single_error = depolarizing_error(0.001, 1)
two_error = depolarizing_error(0.01, 2)

readout_error = ReadoutError([
    [0.99, 0.01],
    [0.01, 0.99]
])

noise_model.add_all_qubit_quantum_error(
    single_error,
    ["rz", "sx"]
)

noise_model.add_all_qubit_quantum_error(
    two_error,
    ["cx"]
)

noise_model.add_all_qubit_readout_error(
    readout_error
)


simulator = AerSimulator(
    method="density_matrix",
    noise_model=noise_model
)


# ==========================================
# 5. FIDELITY CALCULATION
# ==========================================

def calculate_fidelity(ideal, observed):

    keys = set(ideal) | set(observed)

    coefficient = sum(
        np.sqrt(
            ideal.get(key, 0) *
            observed.get(key, 0)
        )
        for key in keys
    )

    return coefficient ** 2


# ==========================================
# 6. RUN SIMULATION
# ==========================================

def run_experiment(name, circuit, ideal):

    measured = circuit.copy()
    measured.measure_all()

    compiled = transpile(
        measured,
        simulator,
        optimization_level=0
    )

    result = simulator.run(
        compiled,
        shots=SHOTS,
        seed_simulator=42
    ).result()

    counts = result.get_counts()

    total = sum(counts.values())

    observed = {
        key: value / total
        for key, value in counts.items()
    }

    fidelity = calculate_fidelity(
        ideal,
        observed
    )

    print("\n===================================")
    print(name)
    print("===================================")

    print("Shots:", SHOTS)
    print("Distribution fidelity:", round(fidelity, 5))

    print("\nCompiled gate counts:")
    print(compiled.count_ops())

    print("\nMeasurement counts:")
    print(counts)

    return fidelity


# ==========================================
# 7. EXECUTE BOTH EXPERIMENTS
# ==========================================

print("\nSTARTING FINAL T-GATE EXPERIMENT")

clifford_fidelity = run_experiment(
    "CLIFFORD-ONLY CIRCUIT",
    clifford,
    ideal_clifford
)

t_fidelity = run_experiment(
    "T-DOPED CIRCUIT",
    t_doped,
    ideal_t
)


# ==========================================
# 8. FINAL COMPARISON
# ==========================================

difference = t_fidelity - clifford_fidelity

print("\n\n===================================")
print("FINAL T-GATE COMPARISON")
print("===================================")

print(
    "Clifford-only fidelity:",
    round(clifford_fidelity, 5)
)

print(
    "T-doped fidelity:",
    round(t_fidelity, 5)
)

print(
    "Difference:",
    round(difference, 5)
)

print("\nIMPORTANT:")
print("Each circuit is compared against its own ideal distribution.")
print("This is output-distribution fidelity, not full state fidelity.")
print("No Paulice checks are claimed for the T-doped circuit.")

print("\nEXPERIMENT COMPLETED!")
