$venvActivate = Join-Path $PSScriptRoot ".venv\Scripts\Activate.ps1"
$ollamaDirectory = Join-Path $env:LOCALAPPDATA "Programs\Ollama"

if (-not (Test-Path $venvActivate)) {
    throw "Project virtual environment activation script not found: $venvActivate"
}

. $venvActivate

if (Test-Path (Join-Path $ollamaDirectory "ollama.exe")) {
    if (($env:Path -split ';') -notcontains $ollamaDirectory) {
        $env:Path = "$env:Path;$ollamaDirectory"
    }
} else {
    Write-Warning "ollama.exe was not found under $ollamaDirectory"
}
