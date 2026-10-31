$ErrorActionPreference = "Stop"
$python = ".\.venv\Scripts\python.exe"
& $python .\src\phase1_baseline.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $python .\src\phase2_slc.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
# The full assignment workflow: noisy baseline plus the SLC/PNA noise sweep.
& $python .\src\phase3_pna.py
exit $LASTEXITCODE
