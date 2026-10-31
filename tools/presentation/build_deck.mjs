import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";
import { applyPresentationChartFont } from "file:///C:/Users/anime/.codex/plugins/cache/openai-primary-runtime/presentations/26.1026.10807/skills/presentations/container_tools/artifact_tool_utils.mjs";

const BUILD = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(BUILD, "..", "..");
const OUT = path.join(ROOT, "presentation");
const PREVIEWS = path.join(OUT, "previews");
const results = JSON.parse(
  await fs.readFile(path.join(ROOT, "results", "phase3_noise_sweep.json"), "utf8"),
);
const rows = results.results;
const n3 = (value) => Number(value.toFixed(3));
const COLORS = {
  navy: "#161616",
  blue: "#0F62FE",
  teal: "#009D9A",
  purple: "#8A3FFC",
  orange: "#FF832B",
  gray: "#525252",
  light: "#F4F4F4",
  grid: "#DDE1E6",
  white: "#FFFFFF",
};

const presentation = Presentation.create({
  slideSize: { width: 1280, height: 720 },
});

function addText(slide, text, x, y, w, h, options = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    typeface: "Arial",
    fontSize: options.size ?? 24,
    bold: options.bold ?? false,
    color: options.color ?? COLORS.navy,
    alignment: options.align ?? "left",
    verticalAlignment: options.vAlign ?? "top",
    wrap: "square",
    autoFit: "shrinkText",
    insets: { left: 0, right: 0, top: 0, bottom: 0 },
  };
  return shape;
}

function newSlide(title, eyebrow = "QISKIT FALL FEST 2026 · TRACK 2") {
  const slide = presentation.slides.add();
  slide.background.fill = COLORS.white;
  addText(slide, eyebrow, 68, 42, 900, 25, {
    size: 16,
    bold: true,
    color: COLORS.blue,
  });
  addText(slide, title, 68, 82, 1144, 65, {
    size: 44,
    bold: true,
    color: COLORS.navy,
  });
  return slide;
}

function setNotes(slide, text) {
  slide.speakerNotes.text = text;
}

// 1. Cover
{
  const slide = presentation.slides.add();
  slide.background.fill = COLORS.light;
  addText(slide, "QISKIT FALL FEST 2026 · TRACKS 1 & 2", 76, 78, 950, 28, {
    size: 18,
    bold: true,
    color: COLORS.blue,
  });
  addText(slide, "Making quantum\nresults more reliable", 76, 174, 970, 190, {
    size: 62,
    bold: true,
    color: COLORS.navy,
  });
  addText(
    slide,
    "Two quantum error studies: spacetime-check post-selection and SLC/PNA mitigation",
    80,
    408,
    920,
    74,
    { size: 27, color: COLORS.gray },
  );
  addText(slide, "Track 1: Pauli checks · Track 2: five-qubit SLC + PNA", 80, 548, 1000, 36, {
    size: 22,
    bold: true,
    color: COLORS.navy,
  });
  setNotes(
    slide,
    "We built a small simulation to see whether error-mitigation tools can recover a useful measurement after noise is added. The assignment asks for SLC, NoiseLearnerV3, and PNA. This deck states clearly where the local simulator uses synthetic calibration rates in place of a hardware noise-learning job.",
  );
}

// 2. Basic terms
{
  const slide = newSlide("The basic idea");
  addText(slide, "A qubit stores quantum information. A gate changes it. Noise makes gates imperfect.", 68, 178, 1090, 65, {
    size: 29,
    bold: true,
    color: COLORS.navy,
  });
  addText(slide, "QUBIT", 72, 300, 205, 35, { size: 18, bold: true, color: COLORS.blue });
  addText(slide, "The quantum version of a bit.", 72, 338, 276, 70, { size: 23 });
  addText(slide, "GATE", 430, 300, 205, 35, { size: 18, bold: true, color: COLORS.blue });
  addText(slide, "An operation applied to one or more qubits.", 430, 338, 300, 78, { size: 23 });
  addText(slide, "NOISE", 820, 300, 205, 35, { size: 18, bold: true, color: COLORS.blue });
  addText(slide, "A small unwanted change during an operation.", 820, 338, 325, 78, { size: 23 });
  addText(
    slide,
    "We repeat the same calculation many times and compare the average result with an ideal reference.",
    72,
    520,
    1040,
    72,
    { size: 24, color: COLORS.gray },
  );
  setNotes(slide, "Keep the explanation simple: the project does not require the audience to know quantum mechanics. A measurement is an average from repeated simulated runs.");
}

// 3. Experiment setup
{
  const slide = newSlide("The experiment");
  addText(slide, "Circuit", 72, 187, 180, 36, { size: 19, bold: true, color: COLORS.blue });
  addText(slide, "5 qubits in a chain, with 8 CZ entangling gates.", 72, 226, 500, 72, { size: 26 });
  addText(slide, "Measurement", 670, 187, 250, 36, { size: 19, bold: true, color: COLORS.blue });
  addText(slide, "Average X value of the center qubit, estimated with Qiskit’s Estimator primitive.", 670, 226, 500, 84, { size: 24 });
  addText(slide, "Comparison", 72, 365, 220, 36, { size: 19, bold: true, color: COLORS.blue });
  addText(slide, "Ideal simulation vs. simulated noisy circuit, then full PNA vs. SLC-selected PNA.", 72, 404, 500, 105, { size: 24 });
  addText(slide, "Noise levels", 670, 365, 250, 36, { size: 19, bold: true, color: COLORS.blue });
  addText(slide, "0.5×, 1× and 2× the same modeled error rates.", 670, 404, 500, 80, { size: 24 });
  addText(slide, "State fidelity is calculated directly from the simulator’s density matrix.", 72, 564, 1090, 42, { size: 21, color: COLORS.gray });
  setNotes(slide, "The center-qubit X measurement is the quantity that PNA corrects. We also calculate exact state fidelity from the simulator's density matrix as a separate measure of how much the whole state was changed.");
}

// 4. Workflow
{
  const slide = newSlide("How the tools fit together");
  addText(slide, "1  Estimate errors", 72, 184, 320, 36, { size: 25, bold: true, color: COLORS.blue });
  addText(slide, "Use a known, simulated calibration model for this local experiment.", 390, 184, 780, 46, { size: 22 });
  addText(slide, "2  Focus the work", 72, 253, 320, 36, { size: 25, bold: true, color: COLORS.teal });
  addText(slide, "SLC ranks errors by how much they can affect the chosen measurement.", 390, 253, 780, 46, { size: 22 });
  addText(slide, "3  Correct the result", 72, 322, 320, 36, { size: 25, bold: true, color: COLORS.purple });
  addText(slide, "PNA folds the modeled correction into the measured quantity.", 390, 322, 780, 46, { size: 22 });
  addText(slide, "Why not NoiseLearnerV3 here?", 72, 422, 650, 40, { size: 26, bold: true });
  addText(
    slide,
    "Its official workflow submits learning jobs to IBM Quantum. No IBM account is configured on this computer, so local rates are simulated inputs, not hardware measurements.",
    72,
    470,
    1080,
    90,
    { size: 22, color: COLORS.gray },
  );
  setNotes(
    slide,
    "SLC assigns importance to candidate Pauli error terms and can trade a bounded bias for lower sampling cost. PNA propagates the inverse of learned noise into an observable. The official NoiseLearnerV3 accepts an IBM Quantum backend/service job; IBM documents that it has no local fake-backend mode. Sources: https://qiskit.github.io/qiskit-addon-slc/guides/quickstart.html ; https://qiskit.github.io/qiskit-addon-pna/tutorials/01_generate_noise_mitigating_observable.html ; https://quantum.cloud.ibm.com/docs/en/guides/migrate-to-client-side-primitives",
  );
}

// 5. SLC overhead reduction
{
  const slide = newSlide("SLC reduced the error model");
  const termValues = rows.map((r) => r.slc_model_term_count);
  const chart = slide.charts.add("bar", {
    position: { left: 70, top: 190, width: 700, height: 400 },
    title: "Error terms retained for PNA",
    titlePlacement: "aboveChart",
    titleTextStyle: { fontSize: 19, bold: true, fill: COLORS.navy },
    categories: rows.map((r) => `${r.noise_scale}× noise`),
    series: [
      { name: "Full model", values: rows.map((r) => r.full_model_term_count), fill: COLORS.gray },
      { name: "After SLC", values: termValues, fill: COLORS.blue },
    ],
    hasLegend: true,
    legend: { position: "bottom", textStyle: { fontSize: 14 } },
    barOptions: { direction: "column", grouping: "clustered", gapWidth: 75 },
    dataLabels: { visible: true, showValue: true, position: "outEnd", textStyle: { fontSize: 13 } },
    yAxis: { min: 0, max: 90, majorUnit: 15, textStyle: { fontSize: 14 }, majorGridlines: { style: "solid", fill: COLORS.grid, width: 1 } },
    xAxis: { textStyle: { fontSize: 14 } },
    chartFill: COLORS.white,
    chartLine: { style: "solid", fill: "none", width: 0 },
    plotAreaFill: COLORS.white,
    plotAreaLine: { style: "solid", fill: "none", width: 0 },
  });
  applyPresentationChartFont(chart, { fontFamily: "Arial" });
  const mid = rows.find((r) => r.noise_scale === 1.0);
  const reduction = Math.round((1 - mid.slc_model_term_count / mid.full_model_term_count) * 100);
  const runtimeReduction = Math.round((1 - mid.slc_pna_preprocessing_seconds / mid.full_pna_preprocessing_seconds) * 100);
  addText(slide, `${reduction}%`, 845, 230, 240, 80, { size: 60, bold: true, color: COLORS.blue });
  addText(slide, "fewer modeled error terms at 1× noise", 845, 310, 315, 62, { size: 22 });
  addText(slide, `${runtimeReduction}%`, 845, 405, 240, 80, { size: 60, bold: true, color: COLORS.teal });
  addText(slide, "less PNA setup time in this small run", 845, 485, 315, 62, { size: 22 });
  addText(slide, `At 1× noise, the SLC bias bound was ${mid.slc_bias_bound.toFixed(3)} (under the 0.05 limit we set).`, 72, 615, 1100, 30, { size: 18, color: COLORS.gray });
  setNotes(slide, `At the middle noise setting, the synthetic model included ${mid.full_model_term_count} candidate error terms. SLC kept ${mid.slc_model_term_count} nonzero terms and set a bias bound of ${mid.slc_bias_bound.toFixed(3)}. PNA preprocessing took ${mid.full_pna_preprocessing_seconds.toFixed(2)} seconds with the full model and ${mid.slc_pna_preprocessing_seconds.toFixed(2)} seconds after SLC. The estimated sampling cost changed from ${mid.full_sampling_cost.toFixed(2)} to ${mid.slc_sampling_cost.toFixed(2)}.`);
}

// 6. Accuracy tradeoff
{
  const slide = newSlide("PNA recovered the measured value");
  const chart = slide.charts.add("line", {
    position: { left: 64, top: 178, width: 800, height: 440 },
    title: "Center-qubit X expectation",
    titlePlacement: "aboveChart",
    titleTextStyle: { fontSize: 19, bold: true, fill: COLORS.navy },
    categories: rows.map((r) => `${r.noise_scale}×`),
    series: [
      { name: "Ideal", values: rows.map((r) => n3(r.ideal_expectation)), fill: COLORS.gray },
      { name: "Noisy", values: rows.map((r) => n3(r.noisy_expectation)), fill: COLORS.orange },
      { name: "Full PNA", values: rows.map((r) => n3(r.full_pna_expectation)), fill: COLORS.blue },
      { name: "SLC + PNA", values: rows.map((r) => n3(r.slc_plus_pna_expectation)), fill: COLORS.teal },
    ],
    hasLegend: true,
    legend: { position: "bottom", textStyle: { fontSize: 13 } },
    lineOptions: { grouping: "standard", smooth: false, varyColors: false },
    dataLabels: { visible: false },
    yAxis: { min: 0.4, max: 1.0, majorUnit: 0.1, textStyle: { fontSize: 14 }, majorGridlines: { style: "solid", fill: COLORS.grid, width: 1 } },
    xAxis: { textStyle: { fontSize: 14 } },
    chartFill: COLORS.white,
    chartLine: { style: "solid", fill: "none", width: 0 },
    plotAreaFill: COLORS.white,
    plotAreaLine: { style: "solid", fill: "none", width: 0 },
  });
  applyPresentationChartFont(chart, { fontFamily: "Arial" });
  const mid = rows.find((r) => r.noise_scale === 1.0);
  addText(slide, "At 1× noise", 930, 224, 260, 38, { size: 22, bold: true, color: COLORS.gray });
  addText(slide, mid.noisy_expectation.toFixed(3), 930, 273, 230, 58, { size: 42, bold: true, color: COLORS.orange });
  addText(slide, "without correction", 930, 327, 260, 34, { size: 18, color: COLORS.gray });
  addText(slide, mid.full_pna_expectation.toFixed(3), 930, 390, 230, 58, { size: 42, bold: true, color: COLORS.blue });
  addText(slide, "with full PNA", 930, 444, 260, 34, { size: 18, color: COLORS.gray });
  addText(slide, mid.slc_plus_pna_expectation.toFixed(3), 930, 507, 230, 58, { size: 42, bold: true, color: COLORS.teal });
  addText(slide, "with SLC + PNA", 930, 561, 260, 34, { size: 18, color: COLORS.gray });
  setNotes(slide, `The ideal value is ${mid.ideal_expectation.toFixed(3)}. At 1× noise, the uncorrected sampled value was ${mid.noisy_expectation.toFixed(3)}. Full PNA estimated ${mid.full_pna_expectation.toFixed(3)}; SLC-selected PNA estimated ${mid.slc_plus_pna_expectation.toFixed(3)}. SLC saves work but can leave more bias, which is the intended tradeoff.`);
}

// 7. State fidelity
{
  const slide = newSlide("Mitigation raised the fidelity estimates");
  const chart = slide.charts.add("line", {
    position: { left: 75, top: 185, width: 740, height: 410 },
    title: "Ideal-state fidelity by noise strength",
    titlePlacement: "aboveChart",
    titleTextStyle: { fontSize: 19, bold: true, fill: COLORS.navy },
    categories: rows.map((r) => `${r.noise_scale}× noise`),
    series: [
      { name: "Ideal", values: rows.map(() => 1), fill: COLORS.gray },
      { name: "Noisy state", values: rows.map((r) => n3(r.noisy_state_fidelity)), fill: COLORS.purple },
      { name: "Full PNA estimate", values: rows.map((r) => n3(r.full_pna_state_fidelity_estimate)), fill: COLORS.blue },
      { name: "SLC + PNA estimate", values: rows.map((r) => n3(r.slc_plus_pna_state_fidelity_estimate)), fill: COLORS.teal },
    ],
    hasLegend: true,
    legend: { position: "bottom", textStyle: { fontSize: 13 } },
    lineOptions: { grouping: "standard", smooth: false, varyColors: false },
    dataLabels: { visible: false },
    yAxis: { min: 0.4, max: 1.05, majorUnit: 0.1, numberFormatCode: "0.00", textStyle: { fontSize: 14 }, majorGridlines: { style: "solid", fill: COLORS.grid, width: 1 } },
    xAxis: { textStyle: { fontSize: 14 } },
    chartFill: COLORS.white,
    chartLine: { style: "solid", fill: "none", width: 0 },
    plotAreaFill: COLORS.white,
    plotAreaLine: { style: "solid", fill: "none", width: 0 },
  });
  applyPresentationChartFont(chart, { fontFamily: "Arial" });
  const mid = rows.find((r) => r.noise_scale === 1.0);
  addText(slide, "At 1× noise", 895, 230, 260, 36, { size: 21, bold: true, color: COLORS.gray });
  addText(slide, mid.noisy_state_fidelity.toFixed(3), 895, 277, 260, 55, { size: 39, bold: true, color: COLORS.purple });
  addText(slide, "noisy-state fidelity", 895, 330, 270, 31, { size: 18, color: COLORS.gray });
  addText(slide, mid.full_pna_state_fidelity_estimate.toFixed(3), 895, 395, 260, 55, { size: 39, bold: true, color: COLORS.blue });
  addText(slide, "full-PNA projector estimate", 895, 448, 270, 31, { size: 18, color: COLORS.gray });
  addText(slide, mid.slc_plus_pna_state_fidelity_estimate.toFixed(3), 895, 495, 260, 55, { size: 39, bold: true, color: COLORS.teal });
  addText(slide, "SLC + PNA projector estimate", 895, 548, 280, 31, { size: 18, color: COLORS.gray });
  addText(slide, "Corrected projector values are estimates and can exceed 1; physical fidelity cannot.", 75, 625, 1110, 28, { size: 17, color: COLORS.gray });
  setNotes(slide, `The ideal-state fidelity projector is |psi><psi| for the noiseless output. We apply full PNA and SLC + PNA to that projector, then evaluate each corrected observable against the noisy density matrix. At 1x noise, raw fidelity is ${mid.noisy_state_fidelity.toFixed(3)}, full-PNA estimates ${mid.full_pna_state_fidelity_estimate.toFixed(3)}, and SLC + PNA estimates ${mid.slc_plus_pna_state_fidelity_estimate.toFixed(3)}. These approximate correction estimates can exceed the physical maximum of one; interpret them as near ideal rather than literal physical fidelities. The raw noisy-state fidelity is the exact simulator value.`);
}

// 8. Time cost across the noise sweep
{
  const slide = newSlide("SLC lowered setup time across the sweep");
  const chart = slide.charts.add("bar", {
    position: { left: 70, top: 185, width: 760, height: 410 },
    title: "PNA preprocessing time",
    titlePlacement: "aboveChart",
    titleTextStyle: { fontSize: 19, bold: true, fill: COLORS.navy },
    categories: rows.map((r) => `${r.noise_scale}× noise`),
    series: [
      { name: "Full PNA", values: rows.map((r) => Number(r.full_pna_preprocessing_seconds.toFixed(2))), fill: COLORS.gray },
      { name: "SLC + PNA", values: rows.map((r) => Number(r.slc_pna_preprocessing_seconds.toFixed(2))), fill: COLORS.teal },
    ],
    hasLegend: true,
    legend: { position: "bottom", textStyle: { fontSize: 14 } },
    barOptions: { direction: "column", grouping: "clustered", gapWidth: 75 },
    dataLabels: { visible: true, showValue: true, position: "outEnd", numberFormatCode: "0.00", textStyle: { fontSize: 13 } },
    yAxis: { min: 0, max: 1.5, majorUnit: 0.25, title: { text: "Seconds", textStyle: { fontSize: 14 } }, textStyle: { fontSize: 14 }, majorGridlines: { style: "solid", fill: COLORS.grid, width: 1 } },
    xAxis: { textStyle: { fontSize: 14 } },
    chartFill: COLORS.white,
    chartLine: { style: "solid", fill: "none", width: 0 },
    plotAreaFill: COLORS.white,
    plotAreaLine: { style: "solid", fill: "none", width: 0 },
  });
  applyPresentationChartFont(chart, { fontFamily: "Arial" });
  const mid = rows.find((r) => r.noise_scale === 1.0);
  const saving = Math.round((1 - mid.slc_pna_preprocessing_seconds / mid.full_pna_preprocessing_seconds) * 100);
  addText(slide, "At 1× noise", 900, 235, 260, 36, { size: 22, bold: true, color: COLORS.gray });
  addText(slide, `${mid.full_pna_preprocessing_seconds.toFixed(2)} s`, 900, 286, 280, 55, { size: 38, bold: true, color: COLORS.gray });
  addText(slide, "full PNA setup", 900, 340, 280, 31, { size: 18, color: COLORS.gray });
  addText(slide, `${mid.slc_pna_preprocessing_seconds.toFixed(2)} s`, 900, 402, 280, 55, { size: 38, bold: true, color: COLORS.teal });
  addText(slide, `SLC + PNA setup (${saving}% less)`, 900, 456, 300, 54, { size: 18, color: COLORS.gray });
  addText(slide, "Times are local preprocessing measurements, not quantum-hardware run times.", 72, 620, 1120, 34, { size: 18, color: COLORS.gray });
  setNotes(slide, `This chart compares the time needed to prepare the correction calculation at each noise strength. At 1x, SLC plus PNA took ${mid.slc_pna_preprocessing_seconds.toFixed(2)} seconds versus ${mid.full_pna_preprocessing_seconds.toFixed(2)} seconds for full PNA, about ${saving}% less. These are local computer preprocessing times, not QPU execution times.`);
}

// 9. Conclusion and limitation
{
  const slide = newSlide("What we learned");
  addText(slide, "PNA helped", 72, 185, 310, 40, { size: 27, bold: true, color: COLORS.blue });
  addText(slide, "It moved the measured value closer to the ideal result at all three noise levels.", 72, 234, 1020, 60, { size: 24 });
  addText(slide, "SLC traded a little accuracy for lower cost", 72, 348, 650, 40, { size: 27, bold: true, color: COLORS.teal });
  addText(slide, "It dropped low-impact error terms and lowered the estimated sampling cost, with a small allowed bias.", 72, 397, 1020, 66, { size: 24 });
  addText(slide, "Next step for a hardware-ready result", 72, 512, 720, 40, { size: 27, bold: true, color: COLORS.purple });
  addText(slide, "Connect NoiseLearnerV3 to an IBM Quantum backend, then rerun the same workflow with measured rates.", 72, 561, 1060, 62, { size: 23 });
  setNotes(slide, "The local results show the algorithmic flow but are not hardware results because calibration rates are synthetic. The official assignment asks for NoiseLearnerV3 and a simulated noisy backend; official documentation says NoiseLearnerV3 does not have a local testing mode. If an IBM Quantum account and backend become available, replace the synthetic model with the output of the official noise learner. Source: https://quantum.cloud.ibm.com/docs/en/guides/migrate-to-client-side-primitives");
}

// Track 1 section: content recreated from the user-provided deck using this deck's style.
const track1 = (title) => newSlide(title, "QISKIT FALL FEST 2026 · TRACK 1");

// 10. Track 1 cover
{
  const slide = track1("Spacetime checks & error detection");
  addText(slide, "A simulator study of Pauli checks, syndrome filtering, and output distributions.", 72, 190, 1050, 82, { size: 30, bold: true });
  addText(slide, "The experiment inserts checks into a small Clifford circuit, rejects shots with non-zero syndrome, and compares the resulting measurement distributions.", 72, 320, 1060, 105, { size: 25, color: COLORS.gray });
  addText(slide, "DETECT  ·  FILTER  ·  COMPARE", 72, 535, 900, 38, { size: 23, bold: true, color: COLORS.blue });
  setNotes(slide, "This section summarizes the separate Track 1 simulation supplied by the user. Its fidelity values describe classical output distributions, not full quantum-state fidelity.");
}

// 11. The problem
{
  const slide = track1("Why error detection matters");
  addText(slide, "Quantum noise", 72, 190, 320, 36, { size: 20, bold: true, color: COLORS.blue });
  addText(slide, "Gates and measurements can introduce errors that change the output.", 72, 237, 330, 105, { size: 24 });
  addText(slide, "Syndrome evidence", 465, 190, 330, 36, { size: 20, bold: true, color: COLORS.teal });
  addText(slide, "Extra checks can flag some corrupted shots, but add more operations and noise exposure.", 465, 237, 330, 120, { size: 24 });
  addText(slide, "Research question", 860, 190, 330, 36, { size: 20, bold: true, color: COLORS.purple });
  addText(slide, "How does check placement relate to fidelity after post-selection?", 860, 237, 335, 120, { size: 24 });
  addText(slide, "Goal: compare unfiltered and filtered output distributions in a reproducible simulator.", 72, 500, 1090, 70, { size: 25, bold: true });
  setNotes(slide, "Checks can help identify suspicious shots, but they add circuit overhead. This project studies that tradeoff on a small simulator.");
}

// 12. Objective and scope
{
  const slide = track1("What the Track 1 prototype does");
  addText(slide, "EXPERIMENT", 72, 180, 500, 30, { size: 18, bold: true, color: COLORS.blue });
  addText(slide, "• Build a three-qubit Clifford circuit\n• Insert Pauli checks with Qiskit Paulice\n• Inspect support bits and interactions\n• Apply a custom syndrome-parity filter\n• Compare output distributions\n• Run a separate T-doped comparison", 72, 220, 540, 270, { size: 23 });
  addText(slide, "SCOPE", 680, 180, 450, 30, { size: 18, bold: true, color: COLORS.teal });
  addText(slide, "A working simulator prototype, not a hardware experiment or full fault-tolerant logical computation.", 680, 220, 490, 120, { size: 25, bold: true });
  addText(slide, "The T-doped comparison is separate: the documented Paulice workflow is Clifford-focused, so we do not claim validated checks on that circuit.", 680, 370, 490, 135, { size: 22, color: COLORS.gray });
  setNotes(slide, "The supplied Track 1 deck reports an implementation using Paulice and a custom filter. This combined presentation preserves its stated scope boundary.");
}

// 13. Key concepts
{
  const slide = track1("Five terms used in the check experiment");
  const terms = [
    ["Pauli check", "An ancilla-based operation sequence that probes a Pauli-related parity."],
    ["Syndrome", "A parity calculated from measured bits; non-zero marks a shot for rejection."],
    ["Post-selection", "Keep shots that pass the chosen syndrome rule; discard the rest."],
    ["Interaction span", "Instruction-index gap between the first and last recorded check interaction."],
    ["Distribution fidelity", "Squared Bhattacharyya overlap between ideal and observed output probabilities."],
  ];
  const positions = [[72,190],[660,190],[72,330],[660,330],[72,480]];
  terms.forEach(([name, definition], i) => {
    const [x,y] = positions[i];
    addText(slide, name, x, y, 500, 32, { size: 20, bold: true, color: i % 2 ? COLORS.teal : COLORS.blue });
    addText(slide, definition, x, y + 40, 510, 70, { size: 22 });
  });
  setNotes(slide, "Distribution fidelity is a classical output-distribution score. Do not call it logical-state fidelity or full quantum-state fidelity.");
}

// 14. Workflow
{
  const slide = track1("Track 1 experimental workflow");
  const steps = [
    ["1 · Build", "3 data qubits\nClifford gates"],
    ["2 · Generate", "Paulice search\nInsert checks"],
    ["3 · Simulate", "Aer noise model\nSample shots"],
    ["4 · Filter", "Compute parity\nAccept / reject"],
    ["5 · Evaluate", "Compare output\ndistributions"],
  ];
  const xs = [70,305,540,775,1010];
  steps.forEach(([head,body],i) => {
    addText(slide, head, xs[i], 235, 190, 35, { size: 20, bold: true, color: [COLORS.blue,COLORS.teal,COLORS.purple,COLORS.orange,COLORS.blue][i] });
    addText(slide, body, xs[i], 285, 190, 90, { size: 23 });
    if (i < steps.length - 1) addText(slide, "→", xs[i]+190, 280, 42, 42, { size: 28, bold: true, color: COLORS.gray, align: "center" });
  });
  addText(slide, "Tools reported: Python · Qiskit · Qiskit Aer · Qiskit Paulice · NumPy · Matplotlib", 72, 500, 1120, 50, { size: 21, color: COLORS.gray });
  setNotes(slide, "The Track 1 source deck describes a five-stage simulator workflow from circuit construction to distribution comparison.");
}

// 15. Custom syndrome filter
{
  const slide = track1("The custom syndrome-parity filter");
  addText(slide, "For check support (0, 1, 3)", 72, 195, 490, 38, { size: 23, bold: true, color: COLORS.blue });
  addText(slide, "S = c₀ ⊕ c₁ ⊕ c₃", 72, 260, 550, 70, { size: 42, bold: true });
  addText(slide, "S = 0  →  accept the shot", 72, 365, 530, 40, { size: 25, bold: true, color: COLORS.teal });
  addText(slide, "S = 1  →  reject the shot", 72, 420, 530, 40, { size: 25, bold: true, color: COLORS.orange });
  addText(slide, "What the rule does", 680, 195, 460, 35, { size: 20, bold: true, color: COLORS.purple });
  addText(slide, "It reads selected measured bits and computes their XOR parity.", 680, 242, 475, 95, { size: 24 });
  addText(slide, "Important limit", 680, 375, 460, 35, { size: 20, bold: true, color: COLORS.orange });
  addText(slide, "This exact expression is specific to support (0, 1, 3). Other check layouts need support-aware parity rules. Passing a check is not proof a shot is error-free.", 680, 422, 490, 130, { size: 21 });
  setNotes(slide, "XOR means exclusive OR: the parity is one when an odd number of selected bits are one. A zero syndrome is evidence the measured check passed; undetected errors may remain.");
}

// 16. First integrated result
{
  const slide = track1("Post-selection improved the first result");
  const chart = slide.charts.add("bar", {
    position: { left: 70, top: 190, width: 700, height: 390 },
    title: "Output-distribution fidelity · 10,000 shots",
    titlePlacement: "aboveChart",
    titleTextStyle: { fontSize: 19, bold: true, fill: COLORS.navy },
    categories: ["No checks", "Checks, no filter", "Checks + filter"],
    series: [{ name: "Fidelity", values: [0.97536,0.95597,0.98108], fill: COLORS.blue }],
    hasLegend: false,
    barOptions: { direction: "column", grouping: "clustered", gapWidth: 90 },
    dataLabels: { visible: true, showValue: true, position: "outEnd", numberFormatCode: "0.00000", textStyle: { fontSize: 13 } },
    yAxis: { min: 0.94, max: 0.99, majorUnit: 0.01, numberFormatCode: "0.00", textStyle: { fontSize: 14 }, majorGridlines: { style: "solid", fill: COLORS.grid, width: 1 } },
    xAxis: { textStyle: { fontSize: 14 } },
    chartFill: COLORS.white,
    chartLine: { style: "solid", fill: "none", width: 0 },
    plotAreaFill: COLORS.white,
    plotAreaLine: { style: "solid", fill: "none", width: 0 },
  });
  applyPresentationChartFont(chart, { fontFamily: "Arial" });
  addText(slide, "Accepted shots", 840, 220, 300, 30, { size: 19, bold: true, color: COLORS.gray });
  addText(slide, "9,380 / 10,000", 840, 265, 350, 58, { size: 36, bold: true, color: COLORS.teal });
  addText(slide, "93.8% acceptance · 6.2% rejected", 840, 330, 350, 56, { size: 20 });
  addText(slide, "In this run, filtering raised fidelity above the no-check baseline.", 840, 435, 350, 90, { size: 23 });
  setNotes(slide, "Source result: no-check fidelity 0.97536; checks without filtering 0.95597; checks with the custom filter 0.98108. The filter accepted 9,380 of 10,000 shots. This is the result of one simulation run.");
}

// 17. Check configuration spans
{
  const slide = track1("Four check configurations were compared");
  const rows1 = [
    ["Windowed", "22"],
    ["Genetic Seed 1", "16"],
    ["Genetic 7", "9"],
    ["Windowed Genetic", "8"],
  ];
  addText(slide, "Configuration", 72, 195, 510, 34, { size: 18, bold: true, color: COLORS.blue });
  addText(slide, "Reported span", 720, 195, 360, 34, { size: 18, bold: true, color: COLORS.blue });
  rows1.forEach(([name,span],i) => {
    const y=250+i*74;
    addText(slide, name, 72, y, 530, 38, { size: 25, bold: i===1 });
    addText(slide, `${span} instruction positions`, 720, y, 420, 38, { size: 24, color: COLORS.teal });
  });
  addText(slide, "Span = last minus first recorded check-ancilla CX instruction index. It is an instruction-position proxy, not physical time.", 72, 575, 1100, 60, { size: 18, color: COLORS.gray });
  setNotes(slide, "For genetic configurations, other check ancillas may have only one recorded CX interaction. The reported span is for an ancilla with at least two interactions, not a complete multi-check spacetime metric.");
}

// 18. Fidelity by configuration
{
  const slide = track1("Post-selection helped, but did not beat baseline");
  const configs=["Windowed · 22","Genetic 1 · 16","Genetic 7 · 9","Windowed Gen. · 8"];
  const chart=slide.charts.add("line", {
    position:{left:65,top:185,width:810,height:415},
    title:"Output-distribution fidelity by check configuration",
    titlePlacement:"aboveChart",
    titleTextStyle:{fontSize:18,bold:true,fill:COLORS.navy},
    categories:configs,
    series:[
      {name:"Checked, before filtering",values:[0.938,0.950,0.959,0.959],fill:COLORS.orange},
      {name:"After post-selection",values:[0.971,0.97833,0.970,0.9715],fill:COLORS.teal},
      {name:"No-check baseline",values:[0.97958,0.97958,0.97958,0.97958],fill:COLORS.gray},
    ],
    hasLegend:true,legend:{position:"bottom",textStyle:{fontSize:12}},
    lineOptions:{grouping:"standard",smooth:false,varyColors:false},
    dataLabels:{visible:false},
    yAxis:{min:0.92,max:0.99,majorUnit:0.01,numberFormatCode:"0.00",textStyle:{fontSize:13},majorGridlines:{style:"solid",fill:COLORS.grid,width:1}},
    xAxis:{textStyle:{fontSize:12}},
    chartFill:COLORS.white,chartLine:{style:"solid",fill:"none",width:0},plotAreaFill:COLORS.white,plotAreaLine:{style:"solid",fill:"none",width:0},
  });
  applyPresentationChartFont(chart,{fontFamily:"Arial"});
  addText(slide,"Best checked result",920,235,270,30,{size:18,bold:true,color:COLORS.gray});
  addText(slide,"0.97833",920,280,250,52,{size:37,bold:true,color:COLORS.teal});
  addText(slide,"Genetic Seed 1",920,330,250,28,{size:18});
  addText(slide,"No-check baseline",920,415,270,30,{size:18,bold:true,color:COLORS.gray});
  addText(slide,"0.97958",920,460,250,52,{size:37,bold:true,color:COLORS.blue});
  addText(slide,"Plot values rounded to 3 decimals except reported exact values.",72,625,1100,26,{size:16,color:COLORS.gray});
  setNotes(slide,"The source reports the best post-selected result as 0.97833 for Genetic Seed 1 and the no-check baseline as 0.97958. Other plotted values have been recreated approximately from the supplied plot and rounded to three decimals. Post-selection improved each checked configuration, but none beat the no-check baseline in that run.");
}

// 19. Separation relationship
{
  const slide=track1("Greater check separation did not mean higher fidelity");
  const chart=slide.charts.add("line",{
    position:{left:70,top:190,width:720,height:390},
    title:"Reported interaction span vs post-selected fidelity",
    titlePlacement:"aboveChart",titleTextStyle:{fontSize:18,bold:true,fill:COLORS.navy},
    categories:["8","9","16","22"],
    series:[
      {name:"Configuration",values:[0.9715,0.9702,0.97833,0.9712],fill:COLORS.purple},
      {name:"No-check baseline",values:[0.97958,0.97958,0.97958,0.97958],fill:COLORS.gray},
    ],
    hasLegend:true,legend:{position:"bottom",textStyle:{fontSize:13}},lineOptions:{grouping:"standard",smooth:false,varyColors:false},dataLabels:{visible:false},
    yAxis:{min:0.969,max:0.981,majorUnit:0.002,numberFormatCode:"0.000",textStyle:{fontSize:13},majorGridlines:{style:"solid",fill:COLORS.grid,width:1}},
    xAxis:{title:{text:"Instruction positions (span)",textStyle:{fontSize:13}},textStyle:{fontSize:13}},
    chartFill:COLORS.white,chartLine:{style:"solid",fill:"none",width:0},plotAreaFill:COLORS.white,plotAreaLine:{style:"solid",fill:"none",width:0},
  });
  applyPresentationChartFont(chart,{fontFamily:"Arial"});
  addText(slide,"No monotonic trend",850,235,340,35,{size:22,bold:true,color:COLORS.blue});
  addText(slide,"The observed fidelity does not consistently rise or fall as the reported span changes.",850,285,330,100,{size:22});
  addText(slide,"Confounding factors",850,425,340,35,{size:22,bold:true,color:COLORS.teal});
  addText(slide,"Check count, support, and circuit overhead also differ between configurations.",850,475,330,90,{size:22});
  setNotes(slide,"This is an exploratory comparison. Span alone was not isolated, so this plot does not establish that separation causes the fidelity change. Points besides the explicitly reported 0.97833 are approximate readings from the source plot.");
}

// 20. Clifford vs T-doped comparison
{
  const slide=track1("A separate comparison tested a T-doped circuit");
  const chart=slide.charts.add("bar",{
    position:{left:80,top:190,width:680,height:390},
    title:"Output-distribution fidelity · 10,000 shots",
    titlePlacement:"aboveChart",titleTextStyle:{fontSize:19,bold:true,fill:COLORS.navy},
    categories:["Clifford-only","T-doped"],
    series:[{name:"Fidelity",values:[0.97522,0.98104],fill:COLORS.purple}],
    hasLegend:false,barOptions:{direction:"column",grouping:"clustered",gapWidth:100},
    dataLabels:{visible:true,showValue:true,position:"outEnd",numberFormatCode:"0.00000",textStyle:{fontSize:14}},
    yAxis:{min:0.96,max:0.99,majorUnit:0.01,numberFormatCode:"0.00",textStyle:{fontSize:14},majorGridlines:{style:"solid",fill:COLORS.grid,width:1}},xAxis:{textStyle:{fontSize:15}},
    chartFill:COLORS.white,chartLine:{style:"solid",fill:"none",width:0},plotAreaFill:COLORS.white,plotAreaLine:{style:"solid",fill:"none",width:0},
  });
  applyPresentationChartFont(chart,{fontFamily:"Arial"});
  addText(slide,"Observed difference",835,220,330,32,{size:19,bold:true,color:COLORS.gray});
  addText(slide,"+0.00582",835,265,310,56,{size:39,bold:true,color:COLORS.teal});
  addText(slide,"for the T-doped circuit in this run",835,325,320,55,{size:19});
  addText(slide,"This does not show that T gates improve robustness. Each circuit is compared with its own ideal output distribution.",835,430,340,115,{size:21});
  setNotes(slide,"The supplied deck reports Clifford-only fidelity 0.97522 with 2 CX and 9 RZ gates; the T-doped circuit had fidelity 0.98104 with 3 CX and 14 RZ gates. This is a separate simplified-noise simulation, not a controlled claim that T gates improve robustness.");
}

// 21. Limitations
{
  const slide=track1("What this Track 1 study does not establish");
  addText(slide,"SIMULATION LIMITS",72,190,500,30,{size:18,bold:true,color:COLORS.blue});
  addText(slide,"• No hardware run or calibrated hardware noise\n• One run per configuration; uncertainty not measured\n• Zero syndrome can still miss errors\n• Check operations add circuit overhead",72,235,520,240,{size:22});
  addText(slide,"METRIC AND SCOPE LIMITS",665,190,540,30,{size:18,bold:true,color:COLORS.teal});
  addText(slide,"• Fidelity is for classical output distributions, not the full quantum state\n• Span is instruction-index distance, not physical time\n• Multi-check configurations need a complete span metric\n• Paulice workflow is Clifford-focused; T-doped checks were not validated",665,235,540,275,{size:21});
  addText(slide,"Treat the findings as a small exploratory simulator study.",72,570,1080,40,{size:24,bold:true,color:COLORS.purple});
  setNotes(slide,"These limitations are carried over from the provided Track 1 presentation. In particular, the output-distribution fidelity should not be mislabeled as logical-state fidelity.");
}

// 22. Conclusion and next steps
{
  const slide=track1("Track 1 takeaway and next steps");
  addText(slide,"What the study achieved",72,190,490,35,{size:22,bold:true,color:COLORS.blue});
  addText(slide,"A noisy three-qubit Clifford simulation, Paulice-generated checks, a custom syndrome filter, and comparisons across check configurations plus a separate T-doped run.",72,240,510,155,{size:22});
  addText(slide,"What to test next",675,190,490,35,{size:22,bold:true,color:COLORS.teal});
  addText(slide,"Repeat with multiple random seeds and confidence intervals; vary separation while holding support and check count fixed; define a full multi-ancilla metric; test calibrated noise.",675,240,505,170,{size:22});
  addText(slide,"Takeaway: filtering improved the checked output distributions in the reported runs, but the placement study does not isolate a causal effect of separation.",72,500,1090,90,{size:24,bold:true});
  setNotes(slide,"The original study's result is promising but exploratory. Repeated runs and controlled configurations are needed before drawing stronger conclusions.");
}

// 23. Judge questions
{
  const slide=track1("Questions judges may ask");
  const qa=[
    ["What is the fidelity metric?","Squared Bhattacharyya coefficient between ideal and observed classical output distributions."],
    ["Does zero syndrome mean no error?","No. It means the measured parity passed; undetected errors can remain."],
    ["Why did checks lower raw fidelity?","They add operations and depth, increasing noise exposure."],
    ["Does span cause the fidelity change?","Not established. Check support and overhead also varied."],
    ["Why no Paulice checks on the T circuit?","The documented workflow is Clifford-focused; non-Clifford support is future work."],
  ];
  qa.forEach(([q,a],i)=>{
    const col=i%2, row=Math.floor(i/2), x=72+col*590, y=175+row*145;
    addText(slide,q,x,y,540,34,{size:19,bold:true,color:col?COLORS.teal:COLORS.blue});
    addText(slide,a,x,y+43,535,75,{size:20});
  });
  setNotes(slide,"Keep answers precise: the scores describe output distributions, the zero syndrome is not a proof of no error, and the span result is exploratory.");
}

await fs.mkdir(OUT, { recursive: true });
await fs.mkdir(PREVIEWS, { recursive: true });
for (const [index, slide] of presentation.slides.items.entries()) {
  const png = await presentation.export({ slide, format: "png", scale: 1 });
  await fs.writeFile(
    path.join(PREVIEWS, `slide-${String(index + 1).padStart(2, "0")}.png`),
    new Uint8Array(await png.arrayBuffer()),
  );
}
const draftPath = path.join(BUILD, "draft-v5.pptx");
await (await PresentationFile.exportPptx(presentation)).save(draftPath);
console.log(JSON.stringify({ draftPath, slides: presentation.slides.items.length }));
