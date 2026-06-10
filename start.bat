@echo off
setlocal EnableExtensions
chcp 65001 > nul
cd /d "%~dp0"
title Office Health Reminder - Bootstrap

set "QUIET=0"
if /I "%~1"=="-silent" set "QUIET=1"

set "PYTHON_CMD="

where py > nul 2> nul
if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
)

if not defined PYTHON_CMD (
    where python > nul 2> nul
    if not errorlevel 1 (
        set "PYTHON_CMD=python"
    )
)

if not defined PYTHON_CMD (
    echo [setup] Python not found. Trying winget install...
    where winget > nul 2> nul
    if errorlevel 1 (
        echo.
        echo [error] Python and winget were not found.
        echo Please install Python 3.10 or newer, then run this file again.
        echo Download: https://www.python.org/downloads/
        echo.
        if "%QUIET%"=="0" pause
        exit /b 1
    )

    winget install --id Python.Python.3.12 -e --source winget --accept-package-agreements --accept-source-agreements --silent
    if errorlevel 1 (
        echo.
        echo [error] Automatic Python install failed.
        echo Please install Python 3.10 or newer, then run this file again.
        echo Download: https://www.python.org/downloads/
        echo.
        if "%QUIET%"=="0" pause
        exit /b 1
    )

    set "PYTHON_CMD=py -3"
)

call :EnsureVenv
if errorlevel 1 exit /b 1

call :InstallPackages
call :EnsureStartupShortcut
call :StartCpuHelper

echo [start] Starting app...
if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\pythonw.exe" "%~dp0main.py"
) else (
    start "" ".venv\Scripts\python.exe" "%~dp0main.py"
)

echo [done] App started.
timeout /t 2 /nobreak > nul
exit /b 0

:EnsureVenv
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys; print(sys.version)" > nul 2> nul
    if errorlevel 1 (
        echo [setup] Existing virtual environment is invalid. Recreating...
        rmdir /s /q ".venv"
    )
)

if not exist ".venv\Scripts\python.exe" (
    echo [setup] Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo.
        echo [error] Failed to create virtual environment.
        echo.
        if "%QUIET%"=="0" pause
        exit /b 1
    )
)

exit /b 0

:InstallPackages
echo [setup] Installing or updating packages...

".venv\Scripts\python.exe" -m pip install --upgrade pip --disable-pip-version-check > nul
if errorlevel 1 (
    echo [warn] pip upgrade failed. Continuing.
)

if exist "requirements.txt" (
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt --disable-pip-version-check
    if errorlevel 1 (
        echo [warn] Core package install failed. Starting with fallback features.
    )
)

if exist "requirements-optional.txt" (
    ".venv\Scripts\python.exe" -m pip install -r requirements-optional.txt --disable-pip-version-check
    if errorlevel 1 (
        echo [warn] Optional package install failed. Continuing.
    )
)

exit /b 0

:EnsureStartupShortcut
if not exist "ensure_startup_shortcut.ps1" exit /b 0

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ensure_startup_shortcut.ps1"
if errorlevel 1 (
    echo [warn] Could not create startup shortcut. You can still run the app manually.
)

exit /b 0

:StartCpuHelper
if not exist "cpu_temp_helper.ps1" exit /b 0

set "CPU_HELPER_PID_FILE=%TEMP%\health_clock_cpu_helper.pid"
if exist "%CPU_HELPER_PID_FILE%" (
    set /p HELPER_PID=<"%CPU_HELPER_PID_FILE%"
    if not "%HELPER_PID%"=="" (
        tasklist /FI "PID eq %HELPER_PID%" /NH 2>nul | findstr /C:"%HELPER_PID%" >nul
        if not errorlevel 1 exit /b 0
    )
)

start "" powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Start-Process powershell -Verb RunAs -WindowStyle Hidden -ArgumentList '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File \"%~dp0cpu_temp_helper.ps1\"'"
exit /b 0
