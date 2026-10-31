# Qiskit Fall Fest 2026 — Tracks 1 and 2

This project contains two small quantum error studies. Track 1 tests Pauli checks and syndrome filtering in a three-qubit simulator. Track 2 tests SLC and PNA on a five-qubit simulated circuit. All Track 2 noise rates are synthetic local inputs; no IBM hardware calibration was run.

## Start here

1. Read this file for setup and navigation.
2. Run `run_all.ps1` to reproduce the Track 2 baseline, SLC analysis, and SLC + PNA noise sweep.
3. Present `presentation/Tracks 1 and 2 combined - code walkthrough.pptx`. Track 1 comes first, followed by Track 2. The slides now show each track's code workflow.

From Windows PowerShell, install dependencies once and run the Track 2 scripts:

```powershell
py -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
./run_all.ps1
```

## Priority guide

1. **Present:** `presentation/Tracks 1 and 2 combined - code walkthrough.pptx`.
2. **Submit:** `submission/Track 2 submission bundle.zip`.
3. **Reproduce Track 2:** `run_all.ps1`, `src/`, `requirements.txt`, and `results/`.
4. **Review:** `docs/` contains the assignment brief, project log, speaker guide, and likely questions. Slide previews are in `presentation/previews/`.
5. **Track 1 source and supporting code:** `supporting/track1_exploration/` contains the earlier scripts, figures, and source deck in the full project folder. The Track 2 submission ZIP includes the combined presentation and Track 2 source/results.

## Code map

- `run_all.ps1` runs the three Track 2 scripts in order.
- `src/phase1_baseline.py` builds a three-qubit circuit, simulates ideal and noisy runs, and saves its center-qubit Z result.
- `src/phase2_slc.py` builds the five-qubit circuit, generates candidate Pauli errors, calculates SLC bounds, and saves the selected-term and cost summary.
- `src/phase3_pna.py` runs the 0.5×, 1×, and 2× noise sweep. It creates full and SLC-pruned models, applies PNA, estimates center-X and fidelity quantities, and writes `results/phase3_noise_sweep.json`.
- `supporting/track1_exploration/scripts/step7_custom_filter_simulation.py` is the integrated Track 1 filtering example shown in the presentation. Other scripts in that folder explore placements, fidelity comparisons, and the separate T-gate run.
- `package_submission.py` rebuilds the submission ZIP.

## What the results mean

- **Ideal expectation:** reference result from a noise-free simulation.
- **Noisy expectation:** result after modeled errors are added.
- **Full PNA / SLC + PNA:** corrected estimates using all modeled error terms or the SLC-selected subset.
- **SLC bias bound:** maximum allowed estimated bias from dropping lower-impact terms; set to 0.05.
- **Preprocessing time:** local computer time to construct the correction, not quantum-hardware execution time.

NoiseLearnerV3 was not run because no IBM Quantum account/backend was configured. Do not report synthetic rates as hardware measurements. Track 1 reports classical output-distribution fidelity. Track 2 reports noisy-state fidelity and approximate corrected-projector estimates. These metrics are not directly comparable.
