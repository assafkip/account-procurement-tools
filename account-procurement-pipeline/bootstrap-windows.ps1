# No-admin Windows bootstrap for locked-down boxes where MSI installs are blocked
# (error 0x80070659). Downloads a PORTABLE Python (no installer, no admin, extracts
# to your user folder) if none is on PATH, then runs the normal setup.
#
# Run from the account-procurement-pipeline folder:
#   powershell -ExecutionPolicy Bypass -File .\bootstrap-windows.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Test-Python {
    try { $null = & python --version 2>$null; return ($LASTEXITCODE -eq 0) } catch { return $false }
}

if (-not (Test-Python)) {
    $dest = Join-Path $env:USERPROFILE "python-portable"
    if (-not (Test-Path (Join-Path $dest "python.exe"))) {
        Write-Host "No Python on PATH. Fetching portable Python (no admin, no installer)..."
        $url = "https://github.com/astral-sh/python-build-standalone/releases/download/20241016/cpython-3.12.7+20241016-x86_64-pc-windows-msvc-install_only.tar.gz"
        $tgz = Join-Path $env:TEMP "python-portable.tar.gz"
        Invoke-WebRequest $url -OutFile $tgz
        New-Item -ItemType Directory -Force -Path $dest | Out-Null
        tar -xzf $tgz -C $dest --strip-components=1
    }
    $env:Path = "$dest;$dest\Scripts;" + $env:Path
    Write-Host "Using portable Python at $dest"
}

python --version
Write-Host "[1/4] Creating virtualenv (.venv)"
python -m venv .venv
$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

Write-Host "[2/4] Installing dependencies"
& $py -m pip install --upgrade pip
& $py -m pip install -r requirements.txt

Write-Host "[3/4] Installing vendored tgspyder"
& $py -m pip install -e ..\tgspyder

Write-Host "[4/4] Installing offline translation models"
& $py install_models.py

Write-Host ""
Write-Host "Done. Authenticate tgspyder once:"
Write-Host "  .\.venv\Scripts\python.exe -m tgspyder.cli '@admobbygoogleplatform' --chats"
Write-Host "Then run:"
Write-Host "  powershell -ExecutionPolicy Bypass -File .\run.ps1 --channels config\channels.txt"
