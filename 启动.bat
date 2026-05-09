@echo off
setlocal EnableExtensions
cd /d "%~dp0"

title PDF Tools

call :ensure_python
if errorlevel 1 goto fail_python

call :ensure_pip
if errorlevel 1 goto fail_pip

echo.
echo [1/3] Checking dependencies...
"%PYTHON_EXE%" -m pip install --disable-pip-version-check -r "%~dp0requirements.txt"
if errorlevel 1 goto fail_deps

echo.
echo [2/3] Starting PDF Tools...
echo [3/3] The browser should open automatically.
echo If it does not open, copy the http://127.0.0.1:PORT address shown below.
echo.
"%PYTHON_EXE%" "%~dp0app.py"
if errorlevel 1 goto fail_run

goto end

:ensure_python
set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
if exist "%PYTHON_EXE%" (
    "%PYTHON_EXE%" -c "import sys" >nul 2>nul
    if not errorlevel 1 exit /b 0
)

set "BASE_PY="
py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
if not errorlevel 1 set "BASE_PY=py -3"

if not defined BASE_PY (
    python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
    if not errorlevel 1 set "BASE_PY=python"
)

if not defined BASE_PY exit /b 1

echo [0/3] Creating local Python virtual environment...
%BASE_PY% -m venv "%~dp0.venv"
if errorlevel 1 exit /b 1

set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" exit /b 1
"%PYTHON_EXE%" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
exit /b %errorlevel%

:ensure_pip
"%PYTHON_EXE%" -m ensurepip --upgrade >nul 2>nul
"%PYTHON_EXE%" -m pip install --disable-pip-version-check --upgrade pip
exit /b %errorlevel%

:fail_python
echo.
echo Startup failed: Python 3.10 or newer was not found.
echo Install Python first, and enable "Add python.exe to PATH" during setup.
echo Download: https://www.python.org/downloads/
goto pause_fail

:fail_pip
echo.
echo Startup failed: pip could not be initialized.
echo You can delete the .venv folder in this directory, then run this file again.
goto pause_fail

:fail_deps
echo.
echo Startup failed: dependency installation failed.
echo The first run needs internet access. Check the network, then run this file again.
goto pause_fail

:fail_run
echo.
echo Startup failed: the web server did not run correctly.
echo Please send the error text above to the maintainer.
goto pause_fail

:pause_fail
echo.
pause
exit /b 1

:end
echo.
pause
exit /b 0
