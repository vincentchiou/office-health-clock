@echo off
chcp 65001 > nul
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [setup] Creating virtual environment...
    python -m venv .venv
    echo [setup] Installing dependencies...
    .venv\Scripts\pip install -r requirements.txt
    echo [setup] Done.
)

start "" .venv\Scripts\pythonw.exe main.py
