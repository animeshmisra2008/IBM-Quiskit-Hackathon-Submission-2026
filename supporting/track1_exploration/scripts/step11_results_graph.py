import matplotlib.pyplot as plt

# Experimental data
configurations = [
    "Windowed",
    "Genetic 1",
    "Genetic 7",
    "Windowed Genetic"
]

spans = [22, 16, 9, 8]

raw_fidelity = [
    0.93749,
    0.95012,
    0.95883,
    0.95946
]

filtered_fidelity = [
    0.97125,
    0.97833,
    0.97019,
    0.97157
]

baseline = 0.97958


# GRAPH 1: Fidelity comparison

x = range(len(configurations))

plt.figure(figsize=(10, 6))

plt.plot(
    x,
    raw_fidelity,
    marker="o",
    label="Before post-selection"
)

plt.plot(
    x,
    filtered_fidelity,
    marker="o",
    label="After post-selection"
)

plt.axhline(
    y=baseline,
    linestyle="--",
    label="No-check baseline"
)

plt.xticks(x, configurations)
plt.ylabel("Output Distribution Fidelity")
plt.title("Effect of Post-selection on Fidelity")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig("fidelity_comparison.png", dpi=300)

plt.show()


# GRAPH 2: Separation vs filtered fidelity

plt.figure(figsize=(8, 6))

plt.scatter(
    spans,
    filtered_fidelity
)

for i, name in enumerate(configurations):

    plt.annotate(
        name,
        (spans[i], filtered_fidelity[i])
    )

plt.axhline(
    y=baseline,
    linestyle="--",
    label="No-check baseline"
)

plt.xlabel("Interaction Span (Instruction Positions)")
plt.ylabel("Post-selected Distribution Fidelity")

plt.title("Interaction Span vs Post-selected Fidelity")

plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig("span_vs_fidelity.png", dpi=300)

plt.show()

print("Both graphs generated successfully!")