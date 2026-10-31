from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from qiskit_aer.noise import (
    NoiseModel,
    depolarizing_error,
    ReadoutError
)
from qiskit_paulice import add_pauli_checks, NoiseModel as PauliceNoiseModel
from collections import Counter
import numpy as np


SHOTS = 5000


# ==========================================
# 1. ORIGINAL CLIFFORD CIRCUIT
# ==========================================

circuit = QuantumCircuit(3)

circuit.h(0)
circuit.h(1)
circuit.h(2)

circuit.cx(0, 1)
circuit.cx(1, 2)

circuit.s(0)
circuit.h(1)


# ==========================================
# 2. IDEAL OUTPUT DISTRIBUTION
# ==========================================

ideal_state = Statevector.from_instruction(circuit)

ideal_probs = ideal_state.probabilities_dict()

print("\nIDEAL DISTRIBUTION:")
print(ideal_probs)


# ==========================================
# 3. AER NOISE MODEL
# ==========================================

noise_model = NoiseModel()

single_error = depolarizing_error(0.001, 1)
two_error = depolarizing_error(0.01, 2)

readout_error = ReadoutError([
    [0.99, 0.01],
    [0.01, 0.99]
])

noise_model.add_all_qubit_quantum_error(
    single_error, ["rz", "sx", "x"]
)

noise_model.add_all_qubit_quantum_error(
    two_error, ["cx"]
)

noise_model.add_all_qubit_readout_error(readout_error)

simulator = AerSimulator(noise_model=noise_model)


# ==========================================
# 4. FIDELITY CALCULATION
# ==========================================

def calculate_fidelity(ideal, observed):

    keys = set(ideal) | set(observed)

    coefficient = sum(
        np.sqrt(ideal.get(k, 0) * observed.get(k, 0))
        for k in keys
    )

    return coefficient ** 2


def normalize_counts(counts):

    total = sum(counts.values())

    return {
        key: value / total
        for key, value in counts.items()
    }


# ==========================================
# 5. DYNAMIC SYNDROME FILTER
# ==========================================

def get_classical_bit(key, checked_circuit, global_index):

    parts = key.split()

    # Qiskit displays classical registers in reverse order.
    registers = list(reversed(checked_circuit.cregs))

    for part_index, register in enumerate(registers):

        for bit_position, bit in enumerate(register):

            index = checked_circuit.find_bit(bit).index

            if index == global_index:

                return int(
                    parts[part_index][register.size - 1 - bit_position]
                )

    raise ValueError(
        f"Classical bit {global_index} not found."
    )


def custom_postselection(key, checked):

    for support in checked.check_support:

        syndrome = 0

        for global_index in support:

            syndrome ^= get_classical_bit(
                key,
                checked.circuit,
                global_index
            )

        if syndrome != 0:
            return False

    return True


def extract_data_bits(key, checked_circuit):

    # The data measurement register is named "meas".
    registers = list(reversed(checked_circuit.cregs))

    for part_index, register in enumerate(registers):

        if register.name == "meas":
            return key.split()[part_index]

    raise ValueError("Data measurement register not found.")


# ==========================================
# 6. EXPERIMENT CONFIGURATIONS
# ==========================================

experiments = [

    {
        "name": "Windowed",
        "method": "windowed",
        "seed": 42
    },

    {
        "name": "Genetic Seed 1",
        "method": "genetic",
        "seed": 1
    },

    {
        "name": "Genetic Seed 7",
        "method": "genetic",
        "seed": 7
    },

    {
        "name": "Windowed Genetic",
        "method": "windowed_genetic",
        "seed": 42
    }

]


# ==========================================
# 7. BASELINE EXPERIMENT
# ==========================================

baseline_circuit = circuit.copy()
baseline_circuit.measure_all()

compiled = transpile(
    baseline_circuit,
    simulator,
    optimization_level=0
)

result = simulator.run(
    compiled,
    shots=SHOTS
).result()

baseline_counts = result.get_counts()

baseline_distribution = normalize_counts(
    baseline_counts
)

baseline_fidelity = calculate_fidelity(
    ideal_probs,
    baseline_distribution
)

print("\n===================================")
print("BASELINE - NO CHECKS")
print("===================================")

print("Shots:", SHOTS)
print("Fidelity:", round(baseline_fidelity, 5))


# ==========================================
# 8. PAULICE CONFIGURATION
# ==========================================

paulice_noise = PauliceNoiseModel(
    gate_noise=0.01,
    readout_noise=0.01
)


# ==========================================
# 9. RUN EACH CHECK CONFIGURATION
# ==========================================

results_table = []

for experiment in experiments:

    print("\n===================================")
    print(experiment["name"])
    print("===================================")

    try:

        measured_circuit = circuit.copy()
        measured_circuit.measure_all()

        checked_list = add_pauli_checks(
            measured_circuit,
            [0, 1, 2],
            paulice_noise,
            cost="gamma",
            method=experiment["method"],
            seed=experiment["seed"]
        )

        checked = checked_list[-1]

        print("Target qubits:", checked.target_qubits)
        print("Check qubits:", checked.check_qubits)
        print("Check support:", checked.check_support)

        if not checked.check_qubits:
            print("No valid checks found. Skipping.")
            continue

        # Calculate interaction span.
        spans = []

        for ancilla in checked.check_qubits:

            positions = []

            for index, instruction in enumerate(
                checked.circuit.data
            ):

                operation = instruction.operation

                qubits = [
                    checked.circuit.find_bit(q).index
                    for q in instruction.qubits
                ]

                if operation.name == "cx" and ancilla in qubits:
                    positions.append(index)

            if len(positions) >= 2:

                span = positions[-1] - positions[0]
                spans.append(span)

        print("Measurable spans:", spans)

        # Simulate checked circuit.
        compiled = transpile(
            checked.circuit,
            simulator,
            optimization_level=0
        )

        result = simulator.run(
            compiled,
            shots=SHOTS
        ).result()

        counts = result.get_counts()

        # Remove check registers and calculate raw distribution.
        raw_data_counts = Counter()

        for key, value in counts.items():

            data = extract_data_bits(
                key,
                checked.circuit
            )

            raw_data_counts[data] += value

        raw_distribution = normalize_counts(
            raw_data_counts
        )

        raw_fidelity = calculate_fidelity(
            ideal_probs,
            raw_distribution
        )

        # Apply custom syndrome filter.
        accepted_counts = Counter()
        accepted_shots = 0

        for key, value in counts.items():

            if custom_postselection(key, checked):

                data = extract_data_bits(
                    key,
                    checked.circuit
                )

                accepted_counts[data] += value
                accepted_shots += value

        if accepted_shots == 0:
            print("No shots accepted. Skipping fidelity.")
            continue

        filtered_distribution = normalize_counts(
            accepted_counts
        )

        filtered_fidelity = calculate_fidelity(
            ideal_probs,
            filtered_distribution
        )

        acceptance_rate = (
            accepted_shots / SHOTS
        ) * 100

        print("\nRESULTS")
        print("Raw fidelity:", round(raw_fidelity, 5))
        print("Post-selected fidelity:", round(filtered_fidelity, 5))
        print("Accepted shots:", accepted_shots)
        print("Rejected shots:", SHOTS - accepted_shots)
        print("Acceptance rate:", round(acceptance_rate, 2), "%")

        results_table.append({

            "name": experiment["name"],
            "spans": spans,
            "raw": raw_fidelity,
            "filtered": filtered_fidelity,
            "acceptance": acceptance_rate

        })

    except Exception as error:

        print("Experiment failed:", error)


# ==========================================
# 10. FINAL COMPARISON
# ==========================================

print("\n\n===================================")
print("FINAL COMPARISON")
print("===================================")

print("Baseline fidelity:", round(baseline_fidelity, 5))

for result in results_table:

    print("\nConfiguration:", result["name"])
    print("Interaction spans:", result["spans"])
    print("Raw fidelity:", round(result["raw"], 5))
    print("Filtered fidelity:", round(result["filtered"], 5))
    print("Acceptance rate:", round(result["acceptance"], 2), "%")

print("\nEXPERIMENT COMPLETED!")