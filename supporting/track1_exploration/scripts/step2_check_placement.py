from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import (
    NoiseModel as AerNoiseModel,
    depolarizing_error,
    ReadoutError
)

from qiskit_paulice import add_pauli_checks
from qiskit_paulice.noise_models import NoiseModel


# ==========================================
# 1. CREATE THE ORIGINAL CIRCUIT
# ==========================================

circuit = QuantumCircuit(3)

circuit.h(0)
circuit.h(1)
circuit.h(2)

circuit.cx(0, 1)
circuit.cx(1, 2)

circuit.s(0)
circuit.h(1)

circuit.measure_all()


# ==========================================
# 2. CREATE PAULICE NOISE MODEL
# ==========================================

paulice_noise = NoiseModel(
    gate_noise=0.01,
    readout_noise=0.01
)


# ==========================================
# 3. GENERATE DIFFERENT CHECK CONFIGURATIONS
# ==========================================

checked_circuits = add_pauli_checks(
    circuit,
    [0, 1, 2],
    paulice_noise,
    cost="gamma",
    method="windowed",
    seed=42
)


# ==========================================
# 4. CREATE SIMULATOR
# ==========================================

aer_noise = AerNoiseModel()

aer_noise.add_all_qubit_quantum_error(
    depolarizing_error(0.01, 2),
    ["cx"]
)

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


# ==========================================
# 5. TEST EACH CONFIGURATION
# ==========================================

print("\n======================================")
print("SPACETIME CHECK PLACEMENT EXPERIMENT")
print("======================================")

for index, checked in enumerate(checked_circuits):

    print(f"\nEXPERIMENT {index + 1}")
    print("------------------------------")

    number_of_checks = len(checked.check_qubits)

    print("Number of checks:", number_of_checks)
    print("Check qubits:", checked.check_qubits)
    print("Check support:", checked.check_support)

    # Compile circuit
    compiled = transpile(
        checked.circuit,
        simulator,
        basis_gates=["id", "rz", "sx", "cx"],
        optimization_level=0
    )

    # Execute circuit
    result = simulator.run(
        compiled,
        shots=2000,
        seed_simulator=42
    ).result()

    counts = result.get_counts()

    # Post-selection
    postselection = checked.get_postselection_method()

    accepted = {
        bitstring: count
        for bitstring, count in counts.items()
        if not postselection(bitstring).any()
    }

    total_shots = sum(counts.values())
    accepted_shots = sum(accepted.values())

    rejected_shots = total_shots - accepted_shots

    rate = accepted_shots / total_shots * 100

    print("Total shots:", total_shots)
    print("Accepted shots:", accepted_shots)
    print("Rejected shots:", rejected_shots)

    print("Post-selection rate:", round(rate, 2), "%")


print("\n======================================")
print("PLACEMENT EXPERIMENT COMPLETED")
print("======================================")