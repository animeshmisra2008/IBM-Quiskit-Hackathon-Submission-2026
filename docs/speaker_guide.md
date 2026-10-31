# Track 2 — simple speaking guide

Use these as short talking points. You do not need to memorize the technical names.

## 1. Making quantum results more reliable

“We simulated a small quantum program, added errors, and tried two tools that reduce the effect of those errors. The goal was to see whether the answer got closer to the ideal one.”

## 2. The basic idea

“A qubit is the quantum version of a computer bit. A gate is an operation on a qubit, and noise is when that operation does not work perfectly. We repeat the calculation and compare the average answer with a clean reference.”

## 3. The experiment

“We used five simulated qubits connected in a chain. We measured one value from the middle qubit, first without noise and then with three different noise strengths.”

## 4. How the tools fit together

“First we supplied a model of the errors. SLC focuses on the errors that matter most to the measurement. PNA uses that error information to adjust the measured answer.”

“The official NoiseLearnerV3 needs an IBM Quantum job. Since this computer has no IBM Quantum account set up, our local run used simulated calibration numbers instead. We have not presented those as hardware measurements.”

## 5. SLC reduced the error model

“At the middle noise level, we started with 78 possible error terms and kept 52. That reduced the correction setup time by about 6 percent in this run. SLC allows a small, stated accuracy tradeoff to save work.”

## 6. PNA recovered the measured value

“At the middle noise level, the noisy answer was about 0.687, while the ideal answer was about 0.981. PNA moved the estimate to about 0.977. Using SLC first gave about 0.962, a little farther from the ideal but with fewer modeled error terms.”

## 7. Mitigation raised the fidelity estimates

“The whole simulated state became less similar to the ideal state as noise increased. At the middle setting, the SLC + PNA estimate rose from 0.695 to 0.892. The full-PNA projector estimate was 1.004, slightly above one because this correction is approximate; a real fidelity cannot be above one.”

## 8. Setup time across the noise sweep

“We also measured how long it took to prepare the correction. At the middle noise level, SLC plus PNA took about 1.18 seconds, compared with 1.25 seconds for full PNA. Those are local computer times, not hardware run times.”

## 9. What we learned

“PNA made the selected measurement more accurate in this simulation. SLC reduced how much mitigation work we needed, at the cost of a small amount of accuracy. A next step would be to connect NoiseLearnerV3 to an IBM Quantum backend and repeat the run with measured error rates.”

## If someone asks what the acronyms mean

- **SLC:** a way to focus error correction on the errors that can affect the chosen measurement.
- **PNA:** a way to account for modeled errors by adjusting the measurement calculation.
- **NoiseLearnerV3:** IBM’s tool for measuring error rates on an IBM Quantum backend.
