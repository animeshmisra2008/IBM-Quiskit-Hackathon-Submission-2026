import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const BUILD = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(BUILD, "..", "..");
const SKILL_DIR = "C:/Users/anime/.codex/plugins/cache/openai-primary-runtime/presentations/26.1026.10807/skills/presentations";
const FINAL_PPTX = path.join(ROOT, "presentation", "Tracks 1 and 2 combined.pptx");
const stagingDir = path.join(BUILD, ".codex-finalizer");
await fs.mkdir(stagingDir, { recursive: true });
await fs.mkdir(path.dirname(FINAL_PPTX), { recursive: true });

const { finalizePresentation } = await import(pathToFileURL(
  path.join(SKILL_DIR, "container_tools/artifact_tool_utils.mjs"),
).href);
const result = await finalizePresentation({
  explicitTotalSlideCount: 23,
  requiredNativeTableOwnerSlides: [],
  requiredNativeChartOwnerSlides: [5, 6, 7, 8, 16, 18, 19, 20],
  materializeLiteralChartWorkbooks: true,
  workspaceDir: ROOT,
  candidatePath: path.join(BUILD, "draft-v5.pptx"),
  finalPath: FINAL_PPTX,
  pythonExecutable: "C:/Users/anime/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe",
  integrityValidatorPath: path.join(SKILL_DIR, "container_tools/inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(SKILL_DIR, "container_tools/inspect_presentation_layout_geometry.py"),
  layoutArgs: [
    "--expected-slide-size-emu", "12192000,6858000",
    "--validate-bullet-geometry",
    "--validate-heading-fit",
    "--expected-slide-count", "23",
  ],
  fontPolicy: { basis: "design", families: ["Arial"] },
  verifyArtifactToolImport: true,
  receiptPath: path.join(stagingDir, "deck.validation-merged.json"),
});
console.log(JSON.stringify(result, null, 2));
