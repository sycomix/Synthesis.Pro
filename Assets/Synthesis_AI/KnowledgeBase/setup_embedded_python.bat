@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   NightBlade KB - Embedded Python Setup
echo ========================================
echo.
echo This will download a portable Python (no installation needed!)
echo Size: ~10 MB
echo.

REM Check if already exists
if exist "%~dp0python\python.exe" (
    echo Python already embedded! Skipping download.
    goto :populate
)

echo Downloading embedded Python 3.11...
echo.

REM Create temp directory
set "TEMP_DIR=%~dp0temp"
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

REM Download embedded Python from python.org
set "PYTHON_URL=https://www.python.org/ftp/python/3.11.8/python-3.11.8-embed-amd64.zip"
set "PYTHON_ZIP=%TEMP_DIR%\python-embed.zip"

echo Downloading from python.org...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_ZIP%'}"

if not exist "%PYTHON_ZIP%" (
    echo ERROR: Failed to download Python!
    echo.
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo Download complete!
echo.

REM Extract Python
echo Extracting Python...
powershell -Command "& {Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%~dp0python' -Force}"

if not exist "%~dp0python\python.exe" (
    echo ERROR: Failed to extract Python!
    pause
    exit /b 1
)

echo Extraction complete!
echo.

REM Download get-pip.py
echo Downloading pip installer...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%~dp0python\get-pip.py'}"

REM Install pip
echo Installing pip...
"%~dp0python\python.exe" "%~dp0python\get-pip.py" --no-warn-script-location

REM Enable pip in embedded Python by uncommenting import site
echo Configuring embedded Python...
powershell -Command "& {$file='%~dp0python\python311._pth'; if(Test-Path $file){(Get-Content $file) -replace '#import site','import site' | Set-Content $file}}"

echo.
echo Cleaning up...
rmdir /s /q "%TEMP_DIR%" 2>nul

echo.
echo ========================================
echo   Embedded Python Setup Complete!
echo ========================================
echo.

:populate

echo Now populating Knowledge Base...
echo.

REM Run populate script with embedded Python
"%~dp0python\python.exe" "%~dp0populate_kb.py"

if errorlevel 1 (
    echo.
    echo ERROR: Failed to populate Knowledge Base!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Success! Knowledge Base Ready!
echo ========================================
echo.
echo You can now use:
echo   - query.bat "search term"
echo   - troubleshoot.bat "error message"
echo   - api.bat ClassName
echo.
echo No Python installation was needed!
echo Embedded Python is in: KnowledgeBase\python\
echo.
pause
