@echo off
echo ========================================
echo   NightBlade Knowledge Base Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo.
    echo Please install Python 3.7+ from: https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found!
echo.

REM Navigate to KB directory
cd /d "%~dp0"

REM Run population script
echo Creating Knowledge Base...
echo This will take about 10 seconds...
echo.

python populate_kb.py

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Usage:
echo   query.bat "search term"
echo   troubleshoot.bat "error message"
echo   api.bat ClassName MethodName
echo.
pause
