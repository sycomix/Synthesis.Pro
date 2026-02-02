@echo off
REM Quick query wrapper for NightBlade KB
cd /d "%~dp0"

if "%~1"=="" (
    echo Usage: query.bat "search term"
    echo Example: query.bat "MapSpawn"
    pause
    exit /b 1
)

REM Use embedded Python if available, otherwise system Python
if exist "%~dp0python\python.exe" (
    "%~dp0python\python.exe" nightblade_kb.py query %*
) else (
    python nightblade_kb.py query %*
)
pause
