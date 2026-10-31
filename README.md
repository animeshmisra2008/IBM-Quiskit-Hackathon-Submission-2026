# Qiskit Fall Fest 2026 — Track 2

This project demonstrates SLC and PNA error mitigation on a small simulated quantum circuit. Noise rates are synthetic local inputs; no IBM hardware calibration was run.

## Start here

1. Read this file for setup and navigation.
2. Run `run_all.ps1` to reproduce the baseline, SLC analysis, and SLC + PNA noise sweep.
3. Open `presentation/Tracks 1 and 2 combined.pptx` for the combined deck. Speaker notes are in the slides.

From Windows PowerShell, create the Python environment and install dependencies once:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\run_all.ps1
```

## File guide

### Run and code

- `run_all.ps1` — runs the three Python scripts below in order.
- `src/phase1_baseline.py` — compares an ideal and noisy three-qubit circuit.
- `src/phase2_slc.py` — demonstrates SLC error-term selection on the five-qubit circuit.
- `src/phase3_pna.py` — main workflow: runs the five-qubit SLC + PNA noise sweep.
- `requirements.txt` — Python packages needed to run the code.

### Results and presentation

- `results/phase1_baseline.json` — baseline output.
- `results/phase2_slc.json` — standalone SLC output.
- `results/phase3_noise_sweep.json` — main sweep, fidelity estimates, and timing data.
- `presentation/Tracks 1 and 2 combined.pptx` — Track 1 and Track 2 content in the Track 2 visual style.
- `presentation/previews/` — PNG preview of each slide.
- `submission/Track 2 submission bundle.zip` — ready-to-share code, results, notes, brief, and deck.

### Background and build tools

- `docs/assignment_brief.pdf` — original assignment.
- `docs/project_log.md` — experiment notes, results, and requirement check.
- `docs/speaker_guide.md` — plain-language talk track.
- `docs/likely_questions.md` — short answers for presentation questions.
- `package_submission.py` — rebuilds the submission ZIP from the listed project files.

## What the results report

- **Ideal expectation:** reference value from a noise-free simulation.
- **Noisy expectation:** estimate after simulated errors are added.
- **Full PNA / SLC + PNA:** corrected estimates using all modeled errors or the SLC-selected subset.
- **SLC bias bound:** theoretical error allowed by dropping low-impact terms; set to at most 0.05.
- **Preprocessing time:** local computer time to build the correction, not quantum hardware runtime.

The local project implements the primitive-based noisy workflow, observable-specific SLC term selection, PNA, and a 0.5×/1×/2× noise sweep. SLC reduces mitigation terms while the complete five-qubit circuit is simulated. The NoiseLearnerV3 hardware calibration step was skipped because no IBM Quantum account/backend is configured. Do not report synthetic rates as hardware measurements.

The combined deck keeps the two tracks' experiments separate. Track 1 reports classical output-distribution fidelity; Track 2 reports noisy-state fidelity and approximate corrected-projector estimates. These metrics are not directly comparable.
