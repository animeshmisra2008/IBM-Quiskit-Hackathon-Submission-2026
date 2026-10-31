# Likely questions — short answers

## Were these results collected on a real quantum computer?

No. They came from a local simulation. The error rates were simulated calibration inputs, not hardware measurements.

## Why did you not run NoiseLearnerV3?

The official tool submits a learning job to an IBM Quantum backend, and no IBM Quantum account is configured here. The code includes a connection point for using its learned rates when a backend is available.

## What did SLC do?

It estimated which modeled errors could most affect our chosen measurement, then let us ignore some low-impact terms. At the middle noise level, that reduced the nonzero modeled terms from 78 to 52.

## What did PNA do?

It used the error model to adjust the measurement calculation. At the middle noise level, the measured value moved from 0.687 toward the ideal 0.981; full PNA estimated 0.977.

## Why is the PNA fidelity estimate slightly above 1?

The correction is approximate, so its estimate can overshoot. A real fidelity cannot exceed 1; we interpret this result as close to ideal, not as a literal value above 1.

## How did you measure the tradeoff?

We increased the same simulated error rates to 0.5×, 1× and 2×, then recorded the measurement accuracy, SLC’s estimated sampling cost, and local preprocessing time.

## What is the main limitation?

The simulation uses synthetic calibration rates and a small five-qubit circuit. Hardware results may differ, so the next step is to run the learner and workflow with measured rates on an IBM Quantum backend.
