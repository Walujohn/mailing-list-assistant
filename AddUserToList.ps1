param(
  [Parameter(Mandatory=$true)][string]$ListName,
  [Parameter(Mandatory=$true)][string]$Email
)

Write-Host "Pretend-Add: $Email -> list '$ListName'"
# Real script would do the update here.
