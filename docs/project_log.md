# Project log

## Phase 1 — first circuit and baseline

- **Question:** How much does simulated gate noise change a simple circuit result?
- **Circuit:** Three qubits in a short chain, with two CZ entangling gates and single-qubit rotations.
- **Measured quantity:** The average `Z` value of the middle qubit, estimated from 20,000 shots per run.
- **Comparison:** Ideal simulator versus the same circuit with depolarizing noise on CZ gates.
- **Why this first:** It makes the later correction methods measurable without needing quantum-computing background.
- **Results:** see `results/phase1_baseline.json` for the latest seeded run. The script's measured quantity is Z; the later SLC/PNA workflow measures X on the center qubit.

## Phase 2 — identify which errors matter

- Used Qiskit's SLC add-on on a five-qubit chain with eight CZ gates.
- The model generated 156 candidate Pauli error terms. SLC retained 64 for the center-qubit measurement at a bias bound of 0.047 (maximum allowed: 0.05).
- The estimated sampling-cost factor fell by 27% for this standalone SLC run.

## Phase 3 — SLC + PNA noise sweep

- The program accepts a parameterized circuit, a parameter value, and an Aer density-matrix backend. It uses Qiskit's `BackendEstimatorV2` primitive for expectation estimates.
- Latest run values are recorded in `results/phase3_noise_sweep.json`. At 1x noise, the ideal center-qubit X value was 0.981. The sampled noisy result was 0.687; full PNA estimated 0.977; SLC + PNA estimated 0.962.
- At 1x noise, SLC reduced the nonzero modeled terms from 78 to 52 and lowered observable-correction preprocessing from 1.23s to 1.12s. The SLC bias bound was 0.047.
- Across 0.5x, 1x, and 2x noise, noisy-state fidelity was 0.833, 0.695, and 0.488. SLC + PNA projector estimates were 0.931, 0.892, and 0.840. These corrected projector values are approximate estimates, not guaranteed physical fidelities.
- Across 0.5x, 1x, and 2x noise, local observable-correction preprocessing was about 1.18s, 1.23s, and 1.25s for full PNA; SLC + PNA took about 1.11s, 1.12s, and 1.15s. These are local preprocessing measurements, not hardware execution times.
- Exact simulated state fidelity before measurement correction was 0.833 at 0.5x noise, 0.695 at 1x, and 0.488 at 2x.
- We also used PNA on the ideal-output fidelity projector. At 1x, the raw simulated fidelity was 0.695 and the full-PNA projector estimate was 1.004. Approximate mitigation can overshoot 1; treat this as near ideal, not as a physically possible fidelity above 1. The SLC-pruned workflow on the prior slides targets the center-X measurement.
- The error rates are synthetic local inputs. No NoiseLearnerV3 job or hardware execution was possible because no IBM Quantum account is configured.

## Plain-language notes

- A **qubit** is the quantum version of a bit.
- A **gate** is an operation applied to qubits.
- **Noise** means an operation sometimes behaves imperfectly.
- An **expectation value** is an average over many repeated runs, not one single answer.

## Track 2 requirement check

- **Parameterized circuit + primitive + simulated noisy backend:** implemented in `src/phase3_pna.py` with `BackendEstimatorV2` and Aer.
- **SLC localization:** implemented by propagating observable-specific bounds and setting low-impact local Pauli error rates to zero before PNA. The full five-qubit circuit is still simulated; this reduces mitigation terms rather than extracting a smaller physical subcircuit.
- **PNA:** applied to the center-qubit X observable and the ideal-state projector, with full-model and SLC-selected comparisons.
- **Noise sweep and tradeoff:** runs at 0.5x, 1x, and 2x, recording corrected observable/fidelity estimates, sampling-cost estimates, and local preprocessing times.
- **NoiseLearnerV3:** not run. This environment has no IBM Quantum credentials or hardware backend; the committed rates are deterministic synthetic values. Therefore the submission demonstrates the pipeline with a stand-in calibration model, not the required hardware-learned local rates. Replace them with NoiseLearnerV3 output before claiming the full calibration requirement is met.
