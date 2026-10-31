from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError
from qiskit_paulice import NoiseModel as PauliceNoiseModel
from qiskit_paulice import add_pauli_checks


# ==========================================
# 1. EXPERIMENT SETTINGS
# ==========================================

SHOTS = 10000


# ==========================================
# 2. CREATE OUR ORIGINAL CIRCUIT
# ==========================================

def create_circuit():

    circuit = QuantumCircuit(3)

    circuit.h(0)
    circuit.h(1)
    circuit.h(2)

    circuit.cx(0, 1)
    circuit.cx(1, 2)

    circuit.s(0)
    circuit.h(1)

    return circuit


# ==========================================
# 3. CUSTOM POST-SELECTION FILTER
# ==========================================

def custom_postselection(bitstring):

    parts = bitstring.split()

    check_bits = parts[0]
    data_bits = parts[1]

    c0 = int(data_bits[-1])
    c1 = int(data_bits[-2])
    c3 = int(check_bits[-1])

    syndrome = c0 ^ c1 ^ c3

    return syndrome == 0


# ==========================================
# 4. CALCULATE DISTRIBUTION FIDELITY
# ==========================================

def calculate_fidelity(ideal, observed):

    fidelity = 0

    for state in ideal:

        p_ideal = ideal[state]
        p_observed = observed.get(state, 0)

        fidelity += (p_ideal * p_observed) ** 0.5

    return fidelity ** 2


# ==========================================
# 5. CREATE IDEAL OUTPUT DISTRIBUTION
# ==========================================

original_circuit = create_circuit()

ideal_state = Statevector.from_instruction(original_circuit)

ideal_probabilities = ideal_state.probabilities_dict()

print("\nIDEAL OUTPUT DISTRIBUTION")
print(ideal_probabilities)


# ==========================================
# 6. CREATE NOISY SIMULATOR
# ==========================================

aer_noise = NoiseModel()

single_qubit_error = depolarizing_error(0.001, 1)
two_qubit_error = depolarizing_error(0.01, 2)

readout_error = ReadoutError([
    [0.99, 0.01],
    [0.01, 0.99]
])

aer_noise.add_all_qubit_quantum_error(
    single_qubit_error,
    ["rz", "sx", "x"]
)

aer_noise.add_all_qubit_quantum_error(
    two_qubit_error,
    ["cx"]
)

aer_noise.add_all_qubit_readout_error(readout_error)

simulator = AerSimulator(noise_model=aer_noise)


# ==========================================
# 7. EXPERIMENT A: WITHOUT CHECKS
# ==========================================

print("\nRunning Experiment A: No Checks...")

baseline = original_circuit.copy()
baseline.measure_all()

compiled_baseline = transpile(baseline, simulator)

baseline_result = simulator.run(
    compiled_baseline,
    shots=SHOTS
).result()

baseline_counts = baseline_result.get_counts()

baseline_distribution = {
    key: value / SHOTS
    for key, value in baseline_counts.items()
}

baseline_fidelity = calculate_fidelity(
    ideal_probabilities,
    baseline_distribution
)


# ==========================================
# 8. INSERT SPACETIME CHECKS
# ==========================================

print("\nGenerating Paulice Spacetime Checks...")

paulice_noise = PauliceNoiseModel(
    gate_noise=0.01,
    readout_noise=0.01
)

measured_circuit = original_circuit.copy()
measured_circuit.measure_all()

checked_circuits = add_pauli_checks(
    measured_circuit,
    [0, 1, 2],
    paulice_noise,
    cost="gamma",
    method="windowed",
    seed=42
)

checked = checked_circuits[-1]

print("Check qubits:", checked.check_qubits)
print("Check support:", checked.check_support)


# ==========================================
# 9. EXPERIMENT B: WITH CHECKS
#    BUT WITHOUT POST-SELECTION
# ==========================================

print("\nRunning Experiment B: Checks Without Filtering...")

compiled_checked = transpile(
    checked.circuit,
    simulator
)

checked_result = simulator.run(
    compiled_checked,
    shots=SHOTS
).result()

checked_counts = checked_result.get_counts()


# Extract data-register measurements

raw_data_counts = {}

for bitstring, count in checked_counts.items():

    data_bits = bitstring.split()[1]

    raw_data_counts[data_bits] = (
        raw_data_counts.get(data_bits, 0) + count
    )

raw_distribution = {
    key: value / SHOTS
    for key, value in raw_data_counts.items()
}

raw_fidelity = calculate_fidelity(
    ideal_probabilities,
    raw_distribution
)


# ==========================================
# 10. EXPERIMENT C: CUSTOM POST-SELECTION
# ==========================================

print("\nRunning Experiment C: Custom Post-Selection...")

accepted_counts = {}
accepted_shots = 0
rejected_shots = 0

for bitstring, count in checked_counts.items():

    if custom_postselection(bitstring):

        data_bits = bitstring.split()[1]

        accepted_counts[data_bits] = (
            accepted_counts.get(data_bits, 0) + count
        )

        accepted_shots += count

    else:

        rejected_shots += count


accepted_distribution = {
    key: value / accepted_shots
    for key, value in accepted_counts.items()
}

filtered_fidelity = calculate_fidelity(
    ideal_probabilities,
    accepted_distribution
)


# ==========================================
# 11. DISPLAY FINAL RESULTS
# ==========================================

acceptance_rate = accepted_shots / SHOTS * 100

print("\n======================================")
print("       FINAL EXPERIMENT RESULTS")
print("======================================")

print("\nExperiment A: No Checks")

print("Shots:", SHOTS)
print("Distribution Fidelity:", round(baseline_fidelity, 5))


print("\nExperiment B: Checks Without Filtering")

print("Shots:", SHOTS)
print("Distribution Fidelity:", round(raw_fidelity, 5))


print("\nExperiment C: Custom Post-Selection")

print("Total Shots:", SHOTS)
print("Accepted Shots:", accepted_shots)
print("Rejected Shots:", rejected_shots)

print("Acceptance Rate:", round(acceptance_rate, 2), "%")

print(
    "Distribution Fidelity:",
    round(filtered_fidelity, 5)
)

print("\n======================================")
print("              COMPARISON")
print("======================================")

print("No Checks:              ", round(baseline_fidelity, 5))
print("Checks Without Filtering:", round(raw_fidelity, 5))
print("With Custom Filtering:  ", round(filtered_fidelity, 5))

print("\nExperiment Completed Successfully!")