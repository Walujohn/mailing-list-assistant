param(
  [Parameter(Mandatory=$true)][string]$ListName,
  [Parameter(Mandatory=$true)][string]$Email
)

Write-Host "Pretend-Add: $Email -> list '$ListName'"
# TODO: call your real implementation here
