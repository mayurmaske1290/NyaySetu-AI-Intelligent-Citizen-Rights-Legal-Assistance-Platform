$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"
Set-Location $backend

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    $py = (Get-Command py -ErrorAction SilentlyContinue)
    if ($py) { & py -3.12 -m venv .venv } else { & python -m venv .venv }
}

$python = Join-Path $backend ".venv\Scripts\python.exe"
& $python -m pip install --upgrade pip
& $python -m pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Warning "Created backend/.env. Add your LLM_API_KEY before using real AI."
}

Write-Host "Starting NyaySetu AI backend on http://127.0.0.1:8000"
& $python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
