@echo off
REM Japan Meteorological Agency JSON Desktop Monitor - Windows Launcher
chcp 65001 > nul
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not found. Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

REM Install required packages if missing
pip show PySide6 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Launch Application
start "" pythonw main.py %*
