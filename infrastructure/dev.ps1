[CmdletBinding()]
param(
    [ValidateSet("up", "down", "logs", "config")]
    [string]$Action = "up"
)

$ErrorActionPreference = "Stop"
$composeFile = Join-Path $PSScriptRoot "compose.dev.yml"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker with the Compose plugin is required."
}

$arguments = switch ($Action) {
    "up" { @("compose", "-f", $composeFile, "up", "--build", "--wait") }
    "down" { @("compose", "-f", $composeFile, "down") }
    "logs" { @("compose", "-f", $composeFile, "logs", "--follow") }
    "config" { @("compose", "-f", $composeFile, "config", "--quiet") }
}

& docker @arguments
if ($LASTEXITCODE -ne 0) {
    throw "docker compose failed with exit code $LASTEXITCODE"
}
