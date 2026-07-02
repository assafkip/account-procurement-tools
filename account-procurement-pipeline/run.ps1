# Run the pipeline on Windows. Passes extra args through to pipeline.py.
# Example: powershell -ExecutionPolicy Bypass -File .\run.ps1 --channels config\channels.txt
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Error ".venv not found. Run:  powershell -ExecutionPolicy Bypass -File .\setup.ps1"
    exit 1
}

& $py src\pipeline.py @args
