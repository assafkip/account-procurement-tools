# One-time setup for Windows (AWS): venv, deps, vendored tgspyder, translation models.
# Run from PowerShell:  powershell -ExecutionPolicy Bypass -File .\setup.ps1
# Safe to re-run. The model download needs network (once).
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "[1/4] Creating virtualenv (.venv)"
python -m venv .venv
$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

Write-Host "[2/4] Installing Python dependencies"
& $py -m pip install --upgrade pip
& $py -m pip install -r requirements.txt

Write-Host "[3/4] Installing vendored tgspyder (editable)"
& $py -m pip install -e ..\tgspyder

Write-Host "[4/4] Installing offline translation models (source -> English)"
& $py install_models.py

Write-Host "Done. Authenticate tgspyder once, then run .\run.ps1"
Write-Host "  .\.venv\Scripts\python.exe -m tgspyder.cli '@somechannel' --chats"
