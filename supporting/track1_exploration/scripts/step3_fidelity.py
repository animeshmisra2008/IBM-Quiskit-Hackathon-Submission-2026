import numpy as np

from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector

from qiskit_aer import AerSimulator
from qiskit_aer.noise import (
    NoiseModel as AerNoiseModel,
    depolarizing_error,
    ReadoutError
)

from qiskit_paulice import add_pauli_checks
from qiskit_paulice.noise_models import NoiseModel


# ==========================================
# 1. CREATE THE IDEAL QUANTUM CIRCUIT
# ==========================================

payload = QuantumCircuit(3)

payload.h(0)
payload.h(1)
payload.h(2)

payload.cx(0, 1)
payload.cx(1, 2)

payload.s(0)
payload.h(1)


# Calculate ideal output probabilities
ideal_state = Statevector.from_instruction(payload)

ideal_probs = ideal_state.probabilities_dict()

print("\nIDEAL OUTPUT PROBABILITIES")
print(ideal_probs)


# ==========================================
# 2. CREATE MEASUREMENT CIRCUIT
# ==========================================

circuit = payload.copy()

circuit.measure_all()


# ==========================================
# 3. CREATE PAULICE CHECKS
# ==========================================

paulice_noise = NoiseModel(
    gate_noise=0.01,
    readout_noise=0.01
)

checked_circuits = add_pauli_checks(
    circuit,
    [0, 1, 2],
    paulice_noise,
    cost="gamma",
    method="windowed",
    seed=42
)

checked = checked_circuits[-1]


# ==========================================
# 4. CREATE AER NOISE MODEL
# ==========================================

noise = AerNoiseModel()

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

simulator = AerSimulator(
    method="stabilizer",
    noise_model=noise
)


# ==========================================
# 5. RUN ORIGINAL CIRCUIT
# ==========================================

compiled_original = transpile(
    circuit,
    simulator,
    optimization_level=0
)

original_result = simulator.run(
    compiled_original,
    shots=10000,
    seed_simulator=123
).result()

original_counts = original_result.get_counts()


# ==========================================
# 6. RUN CHECKED CIRCUIT
# ==========================================

compiled_checked = transpile(
    checked.circuit,
    simulator,
    optimization_level=0
)

checked_result = simulator.run(
    compiled_checked,
    shots=10000,
    seed_simulator=123
).result()

checked_counts = checked_result.get_counts()


# ==========================================
# 7. POST-SELECTION
# ==========================================

postselection = checked.get_postselection_method()

accepted_counts = {
    bitstring: count
    for bitstring, count in checked_counts.items()
    if not postselection(bitstring).any()
}


# Extract only the data-qubit measurement bits
def extract_data_counts(counts):

    output = {}

    for bitstring, count in counts.items():

        data_bits = bitstring.split()[-1]

        output[data_bits] = (
            output.get(data_bits, 0) + count
        )

    return output


accepted_data_counts = extract_data_counts(
    accepted_counts
)


# ==========================================
# 8. CALCULATE DISTRIBUTION FIDELITY
# ==========================================

def calculate_distribution_fidelity(
    ideal,
    observed_counts
):

    total = sum(observed_counts.values())

    observed = {
        key: value / total
        for key, value in observed_counts.items()
    }

    all_keys = set(ideal) | set(observed)

    fidelity = sum(
        np.sqrt(
            ideal.get(key, 0) *
            observed.get(key, 0)
        )
        for key in all_keys
    ) ** 2

    return fidelity


baseline_fidelity = calculate_distribution_fidelity(
    ideal_probs,
    original_counts
)

raw_checked_counts = extract_data_counts(
    checked_counts
)

checked_fidelity = calculate_distribution_fidelity(
    ideal_probs,
    raw_checked_counts
)

postselected_fidelity = calculate_distribution_fidelity(
    ideal_probs,
    accepted_data_counts
)


# ==========================================
# 9. DISPLAY RESULTS
# ==========================================

total = sum(checked_counts.values())

accepted = sum(accepted_counts.values())

acceptance_rate = accepted / total * 100


print("\n======================================")
print("       FIDELITY EXPERIMENT")
print("======================================")

print("\nBaseline distribution fidelity:")
print(round(baseline_fidelity, 5))

print("\nChecked distribution fidelity:")
print(round(checked_fidelity, 5))

print("\nPost-selected distribution fidelity:")
print(round(postselected_fidelity, 5))

print("\nTotal shots:", total)
print("Accepted shots:", accepted)

print(
    "Acceptance rate:",
    round(acceptance_rate, 2),
    "%"
)

print("\n======================================")
print("       EXPERIMENT COMPLETED")
print("======================================")