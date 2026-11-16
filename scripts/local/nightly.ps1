# Laptop job: fetch Workday + Oracle boards, commit data/local.json, push.
# Scheduled nightly by Task Scheduler (setup: docs/MAINTAINING.md, "Laptop job setup"). Touches only data/local.json.
# Exits non-zero on any failure, so Task Scheduler's "Last Run Result" shows it, and the Action's
# freshness check emails the owner if the data goes more than 36 hours without a push.
#
# Security: this runs whatever is on origin/main, so anyone with write access can change what runs here.
# Run it under a separate, non-admin Windows account whose git login is a fine-grained token limited to
# this repo (Contents: read and write), not your personal login.
# Continue, not Stop: git writes normal progress to stderr, which PowerShell would otherwise treat as an error
$ErrorActionPreference = "Continue"
Set-Location (Join-Path $PSScriptRoot "..\..")
New-Item -ItemType Directory -Force logs | Out-Null
$log = "logs\nightly-$(Get-Date -Format yyyy-MM-dd).log"
"=== $(Get-Date -Format o)" >> $log

# A dedicated virtual environment, installed from the hashed lock file, so the laptop runs the same
# package versions as the Action and nothing else installed on this machine.
$py = ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    python -m venv .venv *>> $log
    if ($LASTEXITCODE -ne 0) { "could not create .venv" >> $log; exit 2 }
}

git pull --rebase --autostash *>> $log
if ($LASTEXITCODE -ne 0) { "git pull failed" >> $log; exit 3 }
"running commit $(git rev-parse --short HEAD)" >> $log

& $py -m pip install --quiet --require-hashes -r requirements.txt *>> $log
if ($LASTEXITCODE -ne 0) { "pip install failed" >> $log; exit 4 }

& $py scripts/fetch_ats.py --local --workers 4 *>> $log
if ($LASTEXITCODE -ne 0) { "fetch failed" >> $log; exit 1 }

git add data/local.json
git diff --cached --quiet
if ($LASTEXITCODE -eq 0) { "no changes" >> $log; exit 0 }

git commit -m "Laptop refresh $(Get-Date -Format yyyy-MM-dd)" *>> $log
for ($i = 0; $i -lt 3; $i++) {
    git push *>> $log
    if ($LASTEXITCODE -eq 0) { "pushed" >> $log; exit 0 }
    Start-Sleep -Seconds 15
    git pull --rebase --autostash *>> $log   # the Action pushed first; our files never overlap with its files
}
"push failed after 3 attempts" >> $log
exit 5
