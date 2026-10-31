from qiskit import QuantumCircuit
from qiskit_paulice import NoiseModel, add_pauli_checks


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
# 2. PAULICE NOISE MODEL
# ==========================================

noise = NoiseModel(
    gate_noise=0.01,
    readout_noise=0.01
)


# ==========================================
# 3. EXPERIMENT CONFIGURATIONS
# ==========================================

experiments = [
    {
        "name": "Target Qubit 0",
        "targets": [0],
        "method": "windowed"
    },
    {
        "name": "Target Qubit 1",
        "targets": [1],
        "method": "windowed"
    },
    {
        "name": "Target Qubit 2",
        "targets": [2],
        "method": "windowed"
    },
    {
        "name": "Forward Target Order",
        "targets": [0, 1, 2],
        "method": "windowed"
    },
    {
        "name": "Reverse Target Order",
        "targets": [2, 1, 0],
        "method": "windowed"
    }
]


# ==========================================
# 4. RUN PLACEMENT EXPERIMENTS
# ==========================================

for experiment in experiments:

    print("\n===================================")
    print(experiment["name"])
    print("===================================")

    checked_list = add_pauli_checks(
        circuit,
        experiment["targets"],
        noise,
        cost="gamma",
        method=experiment["method"],
        seed=42
    )

    checked = checked_list[-1]

    print("Target qubits:", checked.target_qubits)
    print("Check qubits:", checked.check_qubits)
    print("Check support:", checked.check_support)
    print("Paulice cost:", checked.cost)

    # Find interactions involving each check ancilla

    for ancilla in checked.check_qubits:

        interaction_positions = []

        for index, instruction in enumerate(
            checked.circuit.data
        ):

            operation = instruction.operation
            qubits = [
                checked.circuit.find_bit(q).index
                for q in instruction.qubits
            ]

            if operation.name == "cx" and ancilla in qubits:
                interaction_positions.append(index)

        print(
            f"Ancilla Q{ancilla} interaction positions:",
            interaction_positions
        )

        if len(interaction_positions) >= 2:

            gaps = [
                interaction_positions[i + 1] -
                interaction_positions[i]
                for i in range(len(interaction_positions) - 1)
            ]

            print("Interaction gaps:", gaps)

            print(
                "Total interaction span:",
                interaction_positions[-1] -
                interaction_positions[0]
            )

        else:
            print("Not enough interactions to calculate separation.")


print("\nPLACEMENT EXPERIMENTS COMPLETED!")