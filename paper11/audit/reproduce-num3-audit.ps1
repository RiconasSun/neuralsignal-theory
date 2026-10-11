$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
Push-Location (Split-Path -Parent $root)
try {
    python paper11/audit/validate_num3.py --register-audit
    if ($LASTEXITCODE -ne 0) { throw 'Audit source registration failed' }
    cmd /d /c "python -m unittest discover -s paper11/audit -p test_validate_num3.py -v 2>&1" | Tee-Object paper11/results/M4_amendment3/artifact-audit-tests.txt
    if ($LASTEXITCODE -ne 0) { throw 'Saved-artifact regression failed' }
    python paper11/audit/validate_num3.py
    if ($LASTEXITCODE -ne 0) { throw 'Saved execution identity/coverage validation failed' }
    throw 'NUM3 numerical gate remains FAIL; audit PASS is not scientific PASS; no numerical replay performed'
} finally { Pop-Location }
