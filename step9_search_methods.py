from qiskit import QuantumCircuit
from qiskit_paulice import NoiseModel, add_pauli_checks

# 1. Create the same Clifford circuit
circuit = QuantumCircuit(3)

circuit.h(0)
circuit.h(1)
circuit.h(2)

circuit.cx(0, 1)
circuit.cx(1, 2)

circuit.s(0)
circuit.h(1)

circuit.measure_all()

# 2. Paulice noise model
noise = NoiseModel(
    gate_noise=0.01,
    readout_noise=0.01
)

# 3. Test different methods and seeds
experiments = [
    ("Windowed", "windowed", 42),
    ("Genetic 1", "genetic", 1),
    ("Genetic 2", "genetic", 7),
    ("Genetic 3", "genetic", 21),
    ("Genetic 4", "genetic", 42),
    ("Windowed Genetic", "windowed_genetic", 42)
]

# 4. Run experiments
for name, method, seed in experiments:

    print("\n===================================")
    print(name)
    print("===================================")

    try:
        results = add_pauli_checks(
            circuit,
            [0, 1, 2],
            noise,
            cost="gamma",
            method=method,
            seed=seed
        )

        checked = results[-1]

        print("Method:", method)
        print("Seed:", seed)
        print("Target qubits:", checked.target_qubits)
        print("Check qubits:", checked.check_qubits)
        print("Check support:", checked.check_support)

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

            print("Ancilla:", ancilla)
            print("Interaction positions:", positions)

            if len(positions) >= 2:
                gaps = [
                    positions[i + 1] - positions[i]
                    for i in range(len(positions) - 1)
                ]

                print("Interaction gaps:", gaps)
                print("Total span:", positions[-1] - positions[0])

    except Exception as error:
        print("Experiment failed:", error)

print("\nALL SEARCH EXPERIMENTS COMPLETED!")