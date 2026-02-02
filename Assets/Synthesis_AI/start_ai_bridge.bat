@echo off
echo ================================================
echo Starting AI Chat Bridge for Unity
echo ================================================
echo.

cd /d "%~dp0"
cd ..\..

set PYTHON_PATH=KnowledgeBase\python\python.exe
set SCRIPT_PATH=Assets\Synthesis_Package\ai_chat_bridge.py

if not exist "%PYTHON_PATH%" (
    echo ERROR: Embedded Python not found!
    echo Please run: Assets\Synthesis_Package\setup_ai_bridge.bat
    echo.
    pause
    exit /b 1
)

if not exist "%SCRIPT_PATH%" (
    echo ERROR: AI bridge script not found at %SCRIPT_PATH%
    echo.
    pause
    exit /b 1
)

echo Starting AI Chat Bridge...
echo.
"%PYTHON_PATH%" "%SCRIPT_PATH%"

pause
