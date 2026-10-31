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

## Priority guide

1. **Final deliverables:** presentation/Tracks 1 and 2 combined.pptx and submission/Track 2 submission bundle.zip.
2. **Reproduce the Track 2 work:** 
un_all.ps1, src/, 
equirements.txt, and the saved outputs in 
esults/.
3. **Read and present:** docs/ contains the assignment brief, experiment log, speaker guide, and likely questions. Slide previews are in presentation/previews/.
4. **Supporting Track 1 materials:** supporting/track1_exploration/ groups the earlier Track 1 scripts, figures, and source presentation. supporting/presentation_versions/ contains the Track 2-only reference deck. These are background materials; use the combined deck for the final presentation.

## File guide

- README.md — this setup and navigation guide.
- 
un_all.ps1 — reproduces the baseline, SLC analysis, and SLC + PNA noise sweep.
- src/phase1_baseline.py — ideal versus noisy three-qubit baseline.
- src/phase2_slc.py — SLC error-term selection on the five-qubit circuit.
- src/phase3_pna.py — five-qubit SLC + PNA noise sweep.
- 
esults/ — saved JSON results from each phase.
- presentation/Tracks 1 and 2 combined.pptx — final combined presentation, in the Track 2 visual style.
- submission/Track 2 submission bundle.zip — ready-to-share code, results, notes, brief, and final deck.
- docs/ — assignment brief, project log, speaker guide, and likely questions.
- package_submission.py — rebuilds the submission ZIP.

## What the results report

- **Ideal expectation:** reference value from a noise-free simulation.
- **Noisy expectation:** estimate after simulated errors are added.
- **Full PNA / SLC + PNA:** corrected estimates using all modeled errors or the SLC-selected subset.
- **SLC bias bound:** theoretical error allowed by dropping low-impact terms; set to at most 0.05.
- **Preprocessing time:** local computer time to build the correction, not quantum hardware runtime.

The local project implements the primitive-based noisy workflow, observable-specific SLC term selection, PNA, and a 0.5×/1×/2× noise sweep. SLC reduces mitigation terms while the complete five-qubit circuit is simulated. The NoiseLearnerV3 hardware calibration step was skipped because no IBM Quantum account/backend is configured. Do not report synthetic rates as hardware measurements.

The combined deck keeps the two tracks' experiments separate. Track 1 reports classical output-distribution fidelity; Track 2 reports noisy-state fidelity and approximate corrected-projector estimates. These metrics are not directly comparable.
