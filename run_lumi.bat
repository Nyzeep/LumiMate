@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_EXE="
set "PYTHON_ARGS="

if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
) else if exist "%~dp0..\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0..\.venv\Scripts\python.exe"
) else (
    where python >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON_EXE=python"
    ) else (
        where py >nul 2>nul
        if not errorlevel 1 (
            set "PYTHON_EXE=py"
            set "PYTHON_ARGS=-3"
        )
    )
)

if not defined PYTHON_EXE (
    echo Python interpreter not found.
    echo Install Python 3.10+ or create a virtual environment at .\.venv.
    exit /b 1
)

"%PYTHON_EXE%" %PYTHON_ARGS% "%~dp0main.py" %*
exit /b %ERRORLEVEL%
