$ErrorActionPreference = "Stop"

Write-Host "Running unit tests..."
python -m unittest

Write-Host ""
Write-Host "Installing build dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

Write-Host ""
Write-Host "Building aml-harness.exe..."

pyinstaller `
  --onefile `
  --name aml-harness `
  --console `
  aml_harness\__main__.py

Write-Host ""
Write-Host "Built: dist\aml-harness.exe"
