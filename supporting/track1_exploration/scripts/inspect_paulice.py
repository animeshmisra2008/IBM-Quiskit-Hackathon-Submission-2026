import inspect

from qiskit_paulice import add_pauli_checks

print("\n===== PAULICE FUNCTION INFORMATION =====")

print("\nFunction signature:")
print(inspect.signature(add_pauli_checks))

print("\nFunction documentation:")
print(inspect.getdoc(add_pauli_checks))


print("\n===== CHECKED CIRCUIT INFORMATION =====")

from qiskit import QuantumCircuit
from qiskit_paulice.noise_models import NoiseModel

circuit = QuantumCircuit(3)

circuit.h(0)
circuit.h(1)
circuit.h(2)

circuit.cx(0, 1)
circuit.cx(1, 2)

circuit.s(0)
circuit.h(1)
circuit.measure_all()


noise = NoiseModel(
    gate_noise=0.01,
    readout_noise=0.01
)

checked_circuits = add_pauli_checks(
    circuit,
    [0, 1, 2],
    noise,
    cost="gamma",
    method="windowed",
    seed=42
)

checked = checked_circuits[-1]

print("\nObject type:")
print(type(checked))

print("\nAvailable attributes:")
print(dir(checked))

print("\nObject variables:")
try:
    print(vars(checked))
except TypeError:
    print("No standard object variables available.")

print("\nChecked circuit:")
print(checked)
print("\n===== ACTUAL CHECKED CIRCUIT =====")

print(checked.circuit.draw(output="text"))

print("\n===== CIRCUIT REGISTERS =====")

for register in checked.circuit.cregs:
    print(register.name, ":", register.size)

print("\n===== CIRCUIT OPERATIONS =====")

for index, instruction in enumerate(checked.circuit.data):

    operation = instruction.operation.name

    qubits = [
        checked.circuit.find_bit(q).index
        for q in instruction.qubits
    ]

    clbits = [
        checked.circuit.find_bit(c).index
        for c in instruction.clbits
    ]

    print(
        index,
        "| Gate:", operation,
        "| Qubits:", qubits,
        "| Classical bits:", clbits
    )

print("\n===== PAULICE POST-SELECTION METHOD =====")

accept = checked.get_postselection_method()

print("\nPost-selection function:")
print(accept)

print("\nTesting sample measurement outcomes:")

test_results = [
    "0 000",
    "0 001",
    "0 010",
    "0 100",
    "1 000",
    "1 001",
    "1 010"
]

for result in test_results:
    print(result, "->", accept(result))

for result in test_results:
    print(result, "->", accept(result))
    