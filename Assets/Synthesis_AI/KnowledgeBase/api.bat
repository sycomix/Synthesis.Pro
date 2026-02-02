@echo off
REM Quick API lookup wrapper for NightBlade KB
cd /d "%~dp0"

if "%~1"=="" (
    echo Usage: api.bat ClassName [MethodName]
    echo Example: api.bat CentralNetworkManager StartServer
    pause
    exit /b 1
)

REM Use embedded Python if available, otherwise system Python
if exist "%~dp0python\python.exe" (
    "%~dp0python\python.exe" nightblade_kb.py api %*
) else (
    python nightblade_kb.py api %*
)
pause
