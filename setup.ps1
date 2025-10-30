<# =======================================================================
 mailing-list-assistant — Setup Script (safe / user-scoped)

 What this does (once):
  • Ensures your PowerShell can run your own scripts (CurrentUser scope).
  • Unblocks your profile file (if it exists).
  • Creates a local .venv and installs requirements.
  • Prompts for your OpenAI API key and writes .env.
  • Adds a 'mailing-assistant' command to your PowerShell profile.
  • Backs up your profile before editing and avoids duplicate entries.

 Nothing here runs with admin or touches machine-wide policy.
======================================================================= #>

$ErrorActionPreference = "Stop"

Write-Host "=== mailing-list-assistant setup ===" -ForegroundColor Cyan

# ---- Resolve repo path (folder where this setup.ps1 lives)
$RepoPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# ---- Make script & profile usable (user scope only)
try {
  Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
} catch {
  Write-Warning "Could not set execution policy (CurrentUser). You may need to allow scripts manually."
}

if (Test-Path $PROFILE) {
  try { Unblock-File $PROFILE } catch { Write-Warning "Could not unblock profile: $($_.Exception.Message)" }
}

# ---- Python check
if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
  Write-Error "Python 'py' launcher not found on PATH. Please install Python 3 and re-run setup."
  exit 1
}

# ---- Create venv if missing (local to repo)
$VenvPath = Join-Path $RepoPath ".venv"
if (-not (Test-Path $VenvPath)) {
  Write-Host "Creating virtual environment..." -ForegroundColor Yellow
  & py -3 -m venv $VenvPath
}

# ---- Activate venv for this session
$Activate = Join-Path $VenvPath "Scripts\Activate.ps1"
if (-not (Test-Path $Activate)) {
  Write-Error "Virtual environment activation script not found at: $Activate"
  exit 1
}
Write-Host "Activating virtual environment..."
. $Activate

# ---- Install dependencies
$ReqPath = Join-Path $RepoPath "requirements.txt"
if (-not (Test-Path $ReqPath)) {
  Write-Error "requirements.txt not found at $ReqPath"
  exit 1
}
Write-Host "Installing requirements..." -ForegroundColor Yellow
pip install --disable-pip-version-check -r $ReqPath

# ---- Create and fill .env if missing; prompt for key
$EnvPath      = Join-Path $RepoPath ".env"
$EnvExample   = Join-Path $RepoPath ".env.example"

if (-not (Test-Path $EnvPath)) {
  if (Test-Path $EnvExample) {
    Copy-Item $EnvExample $EnvPath
  } else {
    # Minimal .env if example missing
    @(
      "OPENAI_API_KEY=",
      "OPENAI_MODEL=gpt-4o-mini"
    ) | Set-Content -Path $EnvPath -Encoding UTF8
  }

  Write-Host ""
  Write-Host "Enter your OPENAI_API_KEY (required for LLM; value is stored locally in .env):" -ForegroundColor Yellow
  $apiKey = Read-Host "OPENAI_API_KEY"
  if ($apiKey) {
    (Get-Content $EnvPath) | ForEach-Object {
      if ($_ -match "^OPENAI_API_KEY=") { "OPENAI_API_KEY=$apiKey" } else { $_ }
    } | Set-Content $EnvPath -Encoding UTF8
  } else {
    Write-Warning "OPENAI_API_KEY left blank. The assistant will fail until the key is provided in .env."
  }
}

# ---- Safely add the profile function 'mailing-assistant'
# Markers so we can update/replace cleanly without duplicates
$StartMarker = "# >>> mailing-assistant START"
$EndMarker   = "# >>> mailing-assistant END"

# Build function block
# NOTE: use double-quotes in here-string for $RepoPath expansion now;
#       we escape $ in function scope with backticks so profile can load it literally.
$FunctionBlock = @"
$StartMarker
function mailing-assistant {
  param([switch]`$NoSetup)

  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force | Out-Null
  Push-Location "$RepoPath"

  if (-not `\$NoSetup) {
    if (-not (Test-Path ".\.venv")) {
      py -3 -m venv .venv
    }
    .\.venv\Scripts\Activate.ps1
    pip install --disable-pip-version-check -r .\requirements.txt | Out-Null
  } else {
    .\.venv\Scripts\Activate.ps1
  }

  python .\main.py
  Pop-Location
}
$EndMarker
"@

# Ensure profile file exists; back it up, then replace any prior block
if (-not (Test-Path -Path $PROFILE)) {
  New-Item -ItemType File -Path $PROFILE -Force | Out-Null
}

# Backup profile once per run with timestamp
$ProfileBackup = "$PROFILE.bak.$((Get-Date).ToString('yyyyMMdd_HHmmss'))"
Copy-Item -Path $PROFILE -Destination $ProfileBackup -Force | Out-Null

# Read profile and remove any existing block between markers
$ProfileLines = Get-Content -Path $PROFILE -ErrorAction SilentlyContinue
$inBlock = $false
$Cleaned = foreach ($line in $ProfileLines) {
  if ($line -eq $StartMarker) { $inBlock = $true; continue }
  if ($line -eq $EndMarker)   { $inBlock = $false; continue }
  if (-not $inBlock) { $line }
}

# Write cleaned content back, then append the fresh block
$Cleaned | Set-Content -Path $PROFILE -Encoding UTF8
Add-Content -Path $PROFILE -Value $FunctionBlock

Write-Host ""
Write-Host "Added 'mailing-assistant' command to your PowerShell profile." -ForegroundColor Green
Write-Host "Profile backup saved to: $ProfileBackup" -ForegroundColor DarkGray

Write-Host ""
Write-Host "Setup complete." -ForegroundColor Cyan
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1) Close this PowerShell window." -ForegroundColor Yellow
Write-Host "  2) Open a NEW PowerShell window so your profile reloads." -ForegroundColor Yellow
Write-Host "  3) Type:  mailing-assistant" -ForegroundColor Yellow
Write-Host ""
Write-Host "(From the repo folder, you can also run: .\assistant.ps1)" -ForegroundColor DarkGray

