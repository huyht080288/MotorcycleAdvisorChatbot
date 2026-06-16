@echo off
set PYTHONPATH=%~dp0src
cd /d %~dp0
.venv\Scripts\uvicorn backend.main:app --reload --port 8000 %*
