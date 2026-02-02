@echo off
REM Quick troubleshooting wrapper for NightBlade KB
cd /d "%~dp0"

if "%~1"=="" (
    echo Usage: troubleshoot.bat "error message"
    echo Example: troubleshoot.bat "connection failed"
    pause
    exit /b 1
)

REM Use embedded Python if available, otherwise system Python
if exist "%~dp0python\python.exe" (
    "%~dp0python\python.exe" nightblade_kb.py troubleshoot %*
) else (
    python nightblade_kb.py troubleshoot %*
)
pause
