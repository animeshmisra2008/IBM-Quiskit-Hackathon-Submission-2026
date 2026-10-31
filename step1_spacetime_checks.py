# ==========================================
# SPACETIME QUANTUM ERROR DETECTION
# STEP 1: First Clifford Circuit + Pauli Checks
# ==========================================

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from qiskit_aer.noise import (
    NoiseModel as AerNoiseModel,
    depolarizing_error,
    ReadoutError
)

from qiskit_paulice import add_pauli_checks
from qiskit_paulice.noise_models import NoiseModel


# ------------------------------------------
# 1. CREATE A BASIC QUANTUM CIRCUIT
# ------------------------------------------

circuit = QuantumCircuit(3)

# Create superposition
circuit.h(0)
circuit.h(1)
circuit.h(2)

# Entangle the qubits
circuit.cx(0, 1)
circuit.cx(1, 2)

# Add more Clifford operations
circuit.s(0)
circuit.h(1)

# Measure all qubits
circuit.measure_all()

print("\n===== ORIGINAL QUANTUM CIRCUIT =====")
print(circuit.draw())


# ------------------------------------------
# 2. CREATE A PAULICE NOISE MODEL
# ------------------------------------------

paulice_noise = NoiseModel(
    gate_noise=0.01,
    readout_noise=0.01
)

print("\n===== PAULICE NOISE MODEL =====")
print(paulice_noise)


# ------------------------------------------
# 3. INSERT SPACETIME PAULI CHECKS
# ------------------------------------------

target_qubits = [0, 1, 2]

checked_circuits = add_pauli_checks(
    circuit,
    target_qubits,
    paulice_noise,
    cost="gamma",
    method="windowed",
    seed=42
)

# Select the version containing the maximum
# number of successfully generated checks.
checked_circuit = checked_circuits[-1]

print("\n===== CHECKED QUANTUM CIRCUIT =====")
print(checked_circuit.circuit.draw())

print("\nNumber of checks:", len(checked_circuit.check_qubits))


# ------------------------------------------
# 4. CREATE A NOISY SIMULATOR
# ------------------------------------------

aer_noise = AerNoiseModel()

# Add two-qubit gate errors
aer_noise.add_all_qubit_quantum_error(
    depolarizing_error(0.01, 2),
    ["cx"]
)

# Add measurement errors
aer_noise.add_all_qubit_readout_error(
    ReadoutError([
        [0.99, 0.01],
        [0.01, 0.99]
    ])
)

simulator = AerSimulator(
    method="stabilizer",
    noise_model=aer_noise
)


# ------------------------------------------
# 5. RUN THE ORIGINAL CIRCUIT
# ------------------------------------------

original_isa = transpile(
    circuit,
    simulator,
    basis_gates=["id", "rz", "sx", "cx"],
    optimization_level=0
)

original_result = simulator.run(
    original_isa,
    shots=2000,
    seed_simulator=42
).result()

original_counts = original_result.get_counts()


# ------------------------------------------
# 6. RUN THE CHECKED CIRCUIT
# ------------------------------------------

checked_isa = transpile(
    checked_circuit.circuit,
    simulator,
    basis_gates=["id", "rz", "sx", "cx"],
    optimization_level=0
)

checked_result = simulator.run(
    checked_isa,
    shots=2000,
    seed_simulator=42
).result()

checked_counts = checked_result.get_counts()


# ------------------------------------------
# 7. POST-SELECTION
# ------------------------------------------

postselection_function = (
    checked_circuit.get_postselection_method()
)

postselected_counts = {
    bitstring: count
    for bitstring, count in checked_counts.items()
    if not postselection_function(bitstring).any()
}

total_shots = sum(checked_counts.values())
kept_shots = sum(postselected_counts.values())
discarded_shots = total_shots - kept_shots

postselection_rate = kept_shots / total_shots


# ------------------------------------------
# 8. DISPLAY RESULTS
# ------------------------------------------

print("\n======================================")
print("         EXPERIMENTAL RESULTS")
print("======================================")

print("\nOriginal circuit measurements:")
print(original_counts)

print("\nChecked circuit measurements:")
print(checked_counts)

print("\nPost-selected measurements:")
print(postselected_counts)

print("\nTotal shots:", total_shots)
print("Accepted shots:", kept_shots)
print("Rejected shots:", discarded_shots)

print(
    "\nPost-selection rate:",
    round(postselection_rate * 100, 2),
    "%"
)

print("\n===== STEP 1 COMPLETED =====")