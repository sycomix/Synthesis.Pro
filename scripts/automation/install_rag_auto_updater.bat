@echo off
REM Install RAG Auto Updater to run automatically
REM This creates a Windows Task Scheduler task that runs on login

echo Installing RAG Auto Updater as automatic background service...
echo.

set "SCRIPT_DIR=%~dp0Assets\Synthesis.Pro\Server"
set "PYTHON_EXE=%SCRIPT_DIR%\python\python.exe"
set "UPDATER_SCRIPT=%SCRIPT_DIR%\rag_auto_updater.py"

REM Create scheduled task to run on login
schtasks /create /tn "SynthesisProRAGUpdater" /tr "\"%PYTHON_EXE%\" \"%UPDATER_SCRIPT%\"" /sc onlogon /rl highest /f

if %errorlevel% equ 0 (
    echo.
    echo [OK] RAG Auto Updater installed successfully!
    echo It will start automatically when you log in to Windows.
    echo.
    echo To start it now without rebooting, run: start_rag_auto_updater.bat
    echo To remove it later, run: uninstall_rag_auto_updater.bat
) else (
    echo.
    echo [ERROR] Failed to install. You may need to run this as Administrator.
    echo Right-click this file and select "Run as administrator"
)

echo.
pause
