Write-Host "=== mailing-list-assistant setup ==="
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

if (-Not (Test-Path ".\.venv")) {
  Write-Host "Creating virtual environment..."
  py -3 -m venv .venv
}

Write-Host "Activating virtual environment..."
.\.venv\Scripts\Activate.ps1

Write-Host "Installing requirements..."
pip install -r .\requirements.txt

if (-Not (Test-Path ".\.env")) {
  Copy-Item .\.env.example .\.env
  Write-Host "`nEnter your OPENAI_API_KEY (required for LLM):"
  $apiKey = Read-Host "OPENAI_API_KEY"
  (Get-Content .\.env) | ForEach-Object {
    if ($_ -match "^OPENAI_API_KEY=") {"OPENAI_API_KEY=$apiKey"} else {$_}
  } | Set-Content .\.env
}

Write-Host "`nSetup complete. Run: .\assistant.ps1"
