@echo off
setlocal
set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo Python interpreter not found: %PYTHON_EXE%
    exit /b 1
)

"%PYTHON_EXE%" "%~dp0main.py"
