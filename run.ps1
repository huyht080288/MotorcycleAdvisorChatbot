$env:PYTHONPATH = Join-Path $PSScriptRoot "src"
Set-Location $PSScriptRoot
& .\.venv\Scripts\uvicorn backend.main:app --reload --port 8000 @args
