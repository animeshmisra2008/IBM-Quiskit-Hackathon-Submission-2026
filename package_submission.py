from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

root = Path(__file__).resolve().parent
files = [
    root / "README.md",
    root / "requirements.txt",
    root / "run_all.ps1",
    root / "docs" / "project_log.md",
    root / "docs" / "assignment_brief.pdf",
    root / "src" / "phase1_baseline.py",
    root / "src" / "phase2_slc.py",
    root / "src" / "phase3_pna.py",
    root / "results" / "phase1_baseline.json",
    root / "results" / "phase2_slc.json",
    root / "results" / "phase3_noise_sweep.json",
    root / "docs" / "speaker_guide.md",
    root / "docs" / "likely_questions.md",
    root / "presentation" / "Tracks 1 and 2 combined - code walkthrough.pptx",
]
missing = [str(path) for path in files if not path.is_file()]
if missing:
    raise FileNotFoundError("Missing submission files:\n" + "\n".join(missing))

archive = root / "submission" / "Track 2 submission bundle.zip"
with ZipFile(archive, "w", compression=ZIP_DEFLATED) as bundle:
    for path in files:
        bundle.write(path, "presentation/Tracks 1 and 2 combined.pptx" if path.name == "Tracks 1 and 2 combined - code walkthrough.pptx" else path.relative_to(root))
print(f"Created {archive} with {len(files)} files")
