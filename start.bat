@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Office Health Clock - Preparing environment...

:: ── Args ─────────────────────────────────────────────
set "QUIET=0"
set "CHECK_ONLY=0"

:ParseArgs
if "%~1"=="" goto ArgsDone
if /I "%~1"=="-silent" set "QUIET=1"
if /I "%~1"=="-check" set "CHECK_ONLY=1"
shift
goto ParseArgs

:ArgsDone

:: ── Config ───────────────────────────────────────────
set "PYTHON_CMD="
set "STEP=0"
set "TOTAL_STEPS=6"

if not exist "logs" mkdir "logs" > nul 2> nul
call :Log === bootstrap started ===

:: ── Main ─────────────────────────────────────────────
cls
echo.
echo  ================================================
echo        Office Health Clock - Auto Setup
echo  ================================================
echo.

:: Step 1
set /a STEP+=1
echo  [%STEP%/%TOTAL_STEPS%] Checking Python...
call :FindPython
if defined PYTHON_CMD (
    for /f "tokens=*" %%V in ('%PYTHON_CMD% --version 2^>^&1') do echo          %%V
    echo          [OK] Python found
) else (
    echo          [*] Installing Python 3.12 via winget...
    call :InstallPython
    if errorlevel 1 (
        echo          [X] Python install failed
        echo.
        echo  Please install Python 3.10+ manually:
        echo  https://www.python.org/downloads/
        echo.
        if "%QUIET%"=="0" pause
        exit /b 1
    )
    call :FindPython
    if not defined PYTHON_CMD (
        echo          [X] Python still not found after install
        if "%QUIET%"=="0" pause
        exit /b 1
    )
    echo          [OK] Python installed
)
echo.

:: Step 2
set /a STEP+=1
echo  [%STEP%/%TOTAL_STEPS%] Setting up virtual environment...
call :EnsureVenv
if errorlevel 1 (
    echo          [X] Failed to create virtual environment
    if "%QUIET%"=="0" pause
    exit /b 1
)
echo          [OK] Virtual environment ready
echo.

:: Step 3
set /a STEP+=1
echo  [%STEP%/%TOTAL_STEPS%] Installing core packages (psutil, yt-dlp, pygame)...
call :InstallCorePackages
echo          [OK] Core packages ready
echo.

:: Step 4
set /a STEP+=1
echo  [%STEP%/%TOTAL_STEPS%] Installing GPU monitoring packages...
call :InstallOptionalPackages
echo          [OK] Hardware monitoring ready
echo.

:: Step 5
set /a STEP+=1
echo  [%STEP%/%TOTAL_STEPS%] Checking music playback (ffmpeg)...
call :CheckFfmpeg
if "%HAS_FFMPEG%"=="1" (
    echo          [OK] ffmpeg found
) else (
    echo          [!!] ffmpeg not found - music playback disabled
    echo          Install: winget install Gyan.FFmpeg
)
echo.

:: Step 6
set /a STEP+=1
echo  [%STEP%/%TOTAL_STEPS%] Setting up auto-start on boot...
call :EnsureStartupShortcut
echo          [OK] Startup shortcut configured
echo.

if "%CHECK_ONLY%"=="1" (
    echo  ================================================
    echo   Environment check complete!
    echo  ================================================
    exit /b 0
)

:: ── Start CPU helper ─────────────────────────────────
call :StartCpuHelper

:: ── Launch App ───────────────────────────────────────
echo  ================================================
echo   All checks passed! Starting app...
echo  ================================================
echo.

call :StartApp
exit /b %errorlevel%

:: ══════════════════════════════════════════════════════
::  Python detection & install
:: ══════════════════════════════════════════════════════

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
)
exit /b 0

:InstallPython
where winget > nul 2> nul
if errorlevel 1 (
    call :Log winget not found
    exit /b 1
)
call :Log installing Python via winget
winget install --id Python.Python.3.12 -e --source winget --scope user --silent --accept-package-agreements --accept-source-agreements
if errorlevel 1 (
    call :Log winget install failed
    exit /b 1
)
set "PATH=%LocalAppData%\Programs\Python\Python312;%LocalAppData%\Programs\Python\Python312\Scripts;%PATH%"
exit /b 0

:: ══════════════════════════════════════════════════════
::  Virtual environment
:: ══════════════════════════════════════════════════════

:EnsureVenv
if exist ".venv\Scripts\python.exe" (
    call :CheckVenvHome
    if errorlevel 1 (
        call :Log venv home invalid, removing
        rmdir /s /q ".venv" 2> nul
    ) else (
        ".venv\Scripts\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" > nul 2> nul
        if not errorlevel 1 (
            call :Log venv is valid
            exit /b 0
        )
        call :Log venv version invalid, removing
        rmdir /s /q ".venv" 2> nul
    )
)

call :Log creating new venv
%PYTHON_CMD% -m venv .venv 2> nul
if errorlevel 1 (
    call :Log venv creation failed
    exit /b 1
)
call :Log venv created
exit /b 0

:CheckVenvHome
if not exist ".venv\pyvenv.cfg" exit /b 1
set "VENV_HOME="
for /f "tokens=2 delims==" %%A in ('findstr /B /I "home =" ".venv\pyvenv.cfg" 2^>nul') do set "VENV_HOME=%%A"
if not defined VENV_HOME exit /b 0
call set "VENV_HOME=%%VENV_HOME:~1%%"
if not exist "%VENV_HOME%\python.exe" exit /b 1
exit /b 0

:: ══════════════════════════════════════════════════════
::  Package installation
:: ══════════════════════════════════════════════════════

:InstallCorePackages
".venv\Scripts\python.exe" -m pip --version > nul 2> nul
if errorlevel 1 (
    ".venv\Scripts\python.exe" -m ensurepip --upgrade > nul 2> nul
)

call :CheckCorePackages
if not errorlevel 1 (
    call :Log core packages already installed
    exit /b 0
)

if exist "requirements.txt" (
    call :Log installing core packages
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt --disable-pip-version-check --timeout 30 --retries 3 > nul 2> nul
    if errorlevel 1 (
        call :Log core package install failed, trying individually
        ".venv\Scripts\python.exe" -m pip install psutil --disable-pip-version-check --timeout 30 > nul 2> nul
        ".venv\Scripts\python.exe" -m pip install yt-dlp --disable-pip-version-check --timeout 30 > nul 2> nul
        ".venv\Scripts\python.exe" -m pip install pygame --disable-pip-version-check --timeout 30 > nul 2> nul
    )
)
exit /b 0

:InstallOptionalPackages
if not exist "requirements-optional.txt" exit /b 0

".venv\Scripts\python.exe" -c "import pynvml" > nul 2> nul
if not errorlevel 1 (
    call :Log nvidia-ml-py already installed
    exit /b 0
)

call :Log installing optional packages
".venv\Scripts\python.exe" -m pip install nvidia-ml-py --disable-pip-version-check --timeout 30 --retries 3 > nul 2> nul
if not errorlevel 1 (
    call :Log nvidia-ml-py installed
)

".venv\Scripts\python.exe" -c "import clr" > nul 2> nul
if not errorlevel 1 exit /b 0
".venv\Scripts\python.exe" -m pip install pythonnet --disable-pip-version-check --timeout 60 --retries 2 > nul 2> nul
exit /b 0

:CheckCorePackages
".venv\Scripts\python.exe" -c "import importlib.util; required=['psutil','yt_dlp','pygame']; missing=[m for m in required if importlib.util.find_spec(m) is None]; exit(1 if missing else 0)" > nul 2> nul
exit /b %errorlevel%

:: ══════════════════════════════════════════════════════
::  ffmpeg check
:: ══════════════════════════════════════════════════════

:CheckFfmpeg
set "HAS_FFMPEG=0"
where ffmpeg > nul 2> nul
if not errorlevel 1 (
    set "HAS_FFMPEG=1"
    exit /b 0
)
where ffplay > nul 2> nul
if not errorlevel 1 (
    set "HAS_FFMPEG=1"
    exit /b 0
)
exit /b 0

:: ══════════════════════════════════════════════════════
::  Startup shortcut
:: ══════════════════════════════════════════════════════

:EnsureStartupShortcut
if not exist "ensure_startup_shortcut.ps1" exit /b 0
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ensure_startup_shortcut.ps1" > nul 2> nul
exit /b 0

:: ══════════════════════════════════════════════════════
::  CPU temperature helper
:: ══════════════════════════════════════════════════════

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

:: ══════════════════════════════════════════════════════
::  Launch app
:: ══════════════════════════════════════════════════════

:StartApp
call :Log starting app
if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\pythonw.exe" "%~dp0main.py"
) else (
    start "" ".venv\Scripts\python.exe" "%~dp0main.py"
)
call :Log app started
timeout /t 2 /nobreak > nul
exit /b 0

:: ══════════════════════════════════════════════════════
::  Log
:: ══════════════════════════════════════════════════════

:Log
echo %date% %time% %*>>"logs\bootstrap.log"
exit /b 0
