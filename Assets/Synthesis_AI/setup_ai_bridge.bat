@echo off
echo ================================================
echo AI Chat Bridge Setup
echo ================================================
echo.

cd /d "%~dp0"
cd ..\..

set PYTHON_PATH=KnowledgeBase\python\python.exe

if not exist "%PYTHON_PATH%" (
    echo ERROR: Embedded Python not found!
    echo Please run: KnowledgeBase\setup_kb.bat first
    echo.
    pause
    exit /b 1
)

echo Installing required packages...
echo.

echo Installing anthropic...
"%PYTHON_PATH%" -m pip install anthropic --quiet

echo Installing openai...
"%PYTHON_PATH%" -m pip install openai --quiet

echo Installing google-generativeai (Gemini)...
"%PYTHON_PATH%" -m pip install google-generativeai --quiet

echo Installing requests...
"%PYTHON_PATH%" -m pip install requests --quiet

echo.
echo ================================================
echo Setup Complete!
echo ================================================
echo.
echo Next steps:
echo 1. Edit Assets\Synthesis_Package\ai_config.json
echo 2. Add your API key
echo 3. Run start_ai_bridge.bat
echo.
pause
