@echo off
REM Uninstall RAG Auto Updater

echo Removing RAG Auto Updater from automatic startup...
echo.

schtasks /delete /tn "SynthesisProRAGUpdater" /f

if %errorlevel% equ 0 (
    echo [OK] RAG Auto Updater removed successfully!
) else (
    echo [INFO] Task may not have been installed
)

echo.
pause
