Write-Host "=== mailing-list-assistant setup ==="
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# Resolve repo path (folder where this setup.ps1 lives)
$RepoPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# Create venv if missing
if (-Not (Test-Path (Join-Path $RepoPath ".\.venv"))) {
  Write-Host "Creating virtual environment..."
  py -3 -m venv (Join-Path $RepoPath ".venv")
}

# Activate venv
Write-Host "Activating virtual environment..."
& (Join-Path $RepoPath ".\.venv\Scripts\Activate.ps1")

# Install deps
Write-Host "Installing requirements..."
pip install -r (Join-Path $RepoPath ".\requirements.txt")

# Create .env if missing and prompt for key
$EnvPath = Join-Path $RepoPath ".\.env"
if (-Not (Test-Path $EnvPath)) {
  Copy-Item (Join-Path $RepoPath ".\.env.example") $EnvPath
  Write-Host "`nEnter your OPENAI_API_KEY (required for LLM):"
  $apiKey = Read-Host "OPENAI_API_KEY"
  (Get-Content $EnvPath) | ForEach-Object {
    if ($_ -match "^OPENAI_API_KEY=") { "OPENAI_API_KEY=$apiKey" } else { $_ }
  } | Set-Content $EnvPath
}

# Ensure PowerShell profile exists
if (!(Test-Path -Path $PROFILE)) {
  New-Item -ItemType File -Path $PROFILE -Force | Out-Null
}

# Add a global 'mailing-assistant' function to the user's profile
# NOTE: `${function:...}` must escape the $ with backtick in the here-string
$escapedRepoPath = $RepoPath.Replace('"','`"')  # escape quotes if any
$profileFunc = @"
function mailing-assistant {
  param([switch]`$NoSetup)

  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
  Push-Location "$escapedRepoPath"

  if (-not `$NoSetup) {
    if (-not (Test-Path ".\.venv")) {
      py -3 -m venv .venv
    }
    .\.venv\Scripts\Activate.ps1
    pip install -r .\requirements.txt | Out-Null
  } else {
    .\.venv\Scripts\Activate.ps1
  }

  python .\main.py
  Pop-Location
}
"@

# Append (or replace existing definition)
# Remove old definitions to avoid duplicates
(Get-Content -Path $PROFILE -ErrorAction SilentlyContinue) `
| Where-Object { $_ -notmatch "function\s+mailing-assistant\s*\{" } `
| Set-Content -Path $PROFILE

Add-Content -Path $PROFILE -Value $profileFunc

Write-Host "`nAdded 'mailing-assistant' command to your PowerShell profile."
Write-Host "Close this window and open a new PowerShell, then run:  mailing-assistant"
Write-Host "Or from this folder you can run:  .\assistant.ps1"
