def custom_postselection(bitstring):

    # Separate check bits and data bits
    parts = bitstring.split()

    check_bits = parts[0]
    data_bits = parts[1]

    # Extract the bits used by our check
    c0 = int(data_bits[-1])
    c1 = int(data_bits[-2])
    c3 = int(check_bits[-1])

    # Calculate syndrome
    syndrome = c0 ^ c1 ^ c3

    # Accept only shots with zero syndrome
    return syndrome == 0


# Test our custom filter
test_results = [
    "0 000",
    "0 001",
    "0 010",
    "0 100",
    "1 000",
    "1 001",
    "1 010"
]

print("CUSTOM SPACETIME POST-SELECTION FILTER")
print("--------------------------------------")

for result in test_results:

    decision = custom_postselection(result)

    if decision:
        print(result, "-> ACCEPTED")
    else:
        print(result, "-> REJECTED")