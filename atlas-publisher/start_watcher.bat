@echo off
:: ═══════════════════════════════════════════════════════════════
::  Atlas Watcher — NthDimension Academy
::  Double-click this to start the auto-deploy watcher.
::  Drop HTML files into the pending\ folder to deploy.
:: ═══════════════════════════════════════════════════════════════

title Atlas Watcher — NthDimension Academy

echo.
echo  ████████████████████████████████████████████████
echo   Atlas Watcher — NthDimension Academy
echo   Drop HTML files into pending\ to auto-deploy
echo   Press Ctrl+C to stop
echo  ████████████████████████████████████████████████
echo.

:: Check .env exists
if not exist "%~dp0.env" (
    echo  [ERROR] .env file not found!
    echo  Copy .env.example to .env and set ATLAS_GITHUB_TOKEN=ghp_xxx
    echo.
    pause
    exit /b 1
)

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found in PATH.
    echo  Install Python from python.org and try again.
    pause
    exit /b 1
)

:: Install requests if needed
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo  Installing requests...
    pip install requests
)

:: Start watcher
python "%~dp0atlas_watch.py"

pause
