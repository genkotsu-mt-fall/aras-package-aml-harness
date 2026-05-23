$ErrorActionPreference = "Stop"

Write-Host "Running unit tests..."
python -m unittest

Write-Host ""
Write-Host "Checking good sample..."
python -m aml_harness .\samples\good\base.xml

Write-Host ""
Write-Host "Checking that bad sample fails as expected..."

python -m aml_harness .\samples\bad\missing-id.xml
$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
  Write-Error "Expected bad sample to fail, but it passed."
}

Write-Host ""
Write-Host "All checks completed."
