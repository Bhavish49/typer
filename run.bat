@echo off
title Terminal Speed Typing Test
cd /d "%~dp0"

echo ===================================================
echo           Terminal Speed Typing Test
echo ===================================================
echo.

:: 1. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to your system PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add python.exe to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: 2. Ensure windows-curses is installed on Windows
python -c "import curses" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing windows-curses dependency...
    pip install windows-curses
    echo.
)

:: 3. Launch application
python typer.py %*
