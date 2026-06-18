@echo off
setlocal EnableExtensions
chcp 65001 > nul
cd /d "%~dp0"
title Office Health Reminder - Bootstrap

set "QUIET=0"
set "CHECK_ONLY=0"
set "INSTALL_OPTIONAL=0"

:ParseArgs
if "%~1"=="" goto ArgsDone
if /I "%~1"=="-silent" set "QUIET=1"
if /I "%~1"=="-check" set "CHECK_ONLY=1"
if /I "%~1"=="-optional" set "INSTALL_OPTIONAL=1"
shift
goto ParseArgs

:ArgsDone

set "APP_NAME=Office Health Reminder"
set "PYTHON_CMD="

if not exist "logs" mkdir "logs" > nul 2> nul
call :Log bootstrap started

echo.
echo ========================================
echo  %APP_NAME% - Environment Check
echo ========================================
echo.

call :Log finding python
call :FindPython
if not defined PYTHON_CMD (
    call :Log python not found, trying winget
    call :InstallPython
    if errorlevel 1 exit /b 1
    call :FindPython
)

if not defined PYTHON_CMD (
    echo [error] Python 3.10 or newer is still not available.
    echo Please install Python 3.10 or newer, then run this file again.
    echo Download: https://www.python.org/downloads/
    if "%QUIET%"=="0" pause
    exit /b 1
)

call :Log ensuring venv
call :EnsureVenv
if errorlevel 1 exit /b 1

call :Log checking packages
call :InstallPackages
if errorlevel 1 exit /b 1

if "%CHECK_ONLY%"=="1" (
    echo [done] Environment check completed.
    exit /b 0
)

call :EnsureStartupShortcut
call :StartCpuHelper
call :StartApp
exit /b %errorlevel%

:FindPython
set "PYTHON_CMD="

call :TryPython "%LocalAppData%\Programs\Python\Python312\python.exe"
if defined PYTHON_CMD exit /b 0

call :TryPython "%LocalAppData%\Programs\Python\Python311\python.exe"
if defined PYTHON_CMD exit /b 0

call :TryPython "%LocalAppData%\Programs\Python\Python310\python.exe"
if defined PYTHON_CMD exit /b 0

call :TryPython py -3
if defined PYTHON_CMD exit /b 0

call :TryPython python
if defined PYTHON_CMD exit /b 0

exit /b 0

:TryPython
set "TEST_CMD=%*"
call :Log trying python %TEST_CMD%
%TEST_CMD% -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" > nul 2> nul
if not errorlevel 1 (
    set "PYTHON_CMD=%TEST_CMD%"
    call :Log python selected %TEST_CMD%
    %TEST_CMD% --version
)
exit /b 0

:InstallPython
echo [setup] Python 3.10 or newer was not found.
echo [setup] Trying to install Python 3.12 with winget...

where winget > nul 2> nul
if errorlevel 1 (
    echo.
    echo [error] winget was not found, so Python cannot be installed automatically.
    echo Please install Python 3.10 or newer, then run this file again.
    echo Download: https://www.python.org/downloads/
    echo.
    if "%QUIET%"=="0" pause
    exit /b 1
)

winget install --id Python.Python.3.12 -e --source winget --scope user --silent --accept-package-agreements --accept-source-agreements
if errorlevel 1 (
    echo.
    echo [error] Automatic Python install failed.
    echo Please install Python 3.10 or newer, then run this file again.
    echo Download: https://www.python.org/downloads/
    echo.
    if "%QUIET%"=="0" pause
    exit /b 1
)

exit /b 0

:EnsureVenv
if exist ".venv\Scripts\python.exe" (
    call :CheckVenvHome
    if errorlevel 1 (
        echo [setup] Existing .venv points to a Python path that is missing on this computer.
        echo [setup] Removing old .venv and rebuilding it...
        rmdir /s /q ".venv"
        if exist ".venv" (
            echo [error] Could not remove old .venv. Please close Python windows and run again.
            if "%QUIET%"=="0" pause
            exit /b 1
        )
    )
)

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" > nul 2> nul
    if errorlevel 1 (
        echo [setup] Existing .venv is invalid on this computer.
        echo [setup] Removing old .venv and rebuilding it...
        rmdir /s /q ".venv"
        if exist ".venv" (
            echo [error] Could not remove old .venv. Please close Python windows and run again.
            if "%QUIET%"=="0" pause
            exit /b 1
        )
    )
)

if not exist ".venv\Scripts\python.exe" (
    echo [setup] Creating local Python environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo.
        echo [error] Failed to create local Python environment.
        if "%QUIET%"=="0" pause
        exit /b 1
    )
)

exit /b 0

:CheckVenvHome
if not exist ".venv\pyvenv.cfg" exit /b 1

set "VENV_HOME="
for /f "tokens=2 delims==" %%A in ('findstr /B /I "home =" ".venv\pyvenv.cfg" 2^>nul') do set "VENV_HOME=%%A"
if not defined VENV_HOME exit /b 0
call set "VENV_HOME=%%VENV_HOME:~1%%"
if not exist "%VENV_HOME%\python.exe" exit /b 1
exit /b 0

:InstallPackages
echo [setup] Checking required packages...

call :Log checking pip
".venv\Scripts\python.exe" -m pip --version > nul 2> nul
if errorlevel 1 (
    call :Log pip missing, running ensurepip
    ".venv\Scripts\python.exe" -m ensurepip --upgrade > nul 2> nul
)

call :Log checking core package imports
call :CheckCorePackages
if not errorlevel 1 (
    call :Log core packages ready
    echo [setup] Required packages are ready.
    goto OptionalPackages
)

if exist "requirements.txt" (
    call :Log installing required packages
    echo [setup] Installing required packages...
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt --disable-pip-version-check --timeout 10 --retries 1
    if errorlevel 1 (
        echo.
        echo [warn] Required package install failed. Starting with built-in fallback features.
        exit /b 0
    )
)

:OptionalPackages
if not "%INSTALL_OPTIONAL%"=="1" exit /b 0

if exist "requirements-optional.txt" (
    call :Log installing optional packages
    echo [setup] Installing optional packages...
    ".venv\Scripts\python.exe" -m pip install -r requirements-optional.txt --disable-pip-version-check --timeout 10 --retries 1
    if errorlevel 1 (
        echo [warn] Optional package install failed. Continuing.
    )
)

exit /b 0

:CheckCorePackages
".venv\Scripts\python.exe" -c "import importlib.util, sys; required=['psutil']; missing=[m for m in required if importlib.util.find_spec(m) is None]; print('missing: ' + ', '.join(missing)) if missing else None; raise SystemExit(1 if missing else 0)" > nul 2> nul
exit /b %errorlevel%

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

:StartApp
echo [start] Starting app...
if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\pythonw.exe" "%~dp0main.py"
) else (
    start "" ".venv\Scripts\python.exe" "%~dp0main.py"
)

echo [done] App started.
timeout /t 2 /nobreak > nul
exit /b 0

:Log
echo %date% %time% %*>>"logs\bootstrap.log"
exit /b 0
