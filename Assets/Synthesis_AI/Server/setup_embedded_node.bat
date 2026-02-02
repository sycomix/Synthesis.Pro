@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   Synthesis MCP - Embedded Node.js Setup
echo ========================================
echo.
echo This will download portable Node.js (no installation needed!)
echo Size: ~30 MB
echo.

REM Check if already exists
if exist "%~dp0node\node.exe" (
    echo Node.js already embedded! Skipping download.
    goto :install
)

echo Downloading embedded Node.js 20.11.0...
echo.

REM Create temp directory
set "TEMP_DIR=%~dp0temp"
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

REM Download embedded Node.js from nodejs.org
set "NODE_URL=https://nodejs.org/dist/v20.11.0/node-v20.11.0-win-x64.zip"
set "NODE_ZIP=%TEMP_DIR%\node-embed.zip"

echo Downloading from nodejs.org...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%NODE_URL%' -OutFile '%NODE_ZIP%'}"

if not exist "%NODE_ZIP%" (
    echo ERROR: Failed to download Node.js!
    echo.
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo Download complete!
echo.

REM Extract Node.js
echo Extracting Node.js...
powershell -Command "& {Expand-Archive -Path '%NODE_ZIP%' -DestinationPath '%TEMP_DIR%' -Force}"

REM Move to node folder
echo Moving to node folder...
move "%TEMP_DIR%\node-v20.11.0-win-x64" "%~dp0node"

if not exist "%~dp0node\node.exe" (
    echo ERROR: Failed to extract Node.js!
    pause
    exit /b 1
)

REM Cleanup
echo Cleaning up...
rmdir /s /q "%TEMP_DIR%"

echo.
echo Node.js embedded successfully!
echo.

:install
echo ========================================
echo   Installing MCP Server Dependencies
echo ========================================
echo.
echo Running: npm install
echo.

cd "%~dp0"
"%~dp0node\node.exe" "%~dp0node\node_modules\npm\bin\npm-cli.js" install

if errorlevel 1 (
    echo.
    echo ERROR: npm install failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Building MCP Server
echo ========================================
echo.
echo Running: npm run build
echo.

"%~dp0node\node.exe" "%~dp0node\node_modules\npm\bin\npm-cli.js" run build

if errorlevel 1 (
    echo.
    echo ERROR: npm run build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next Steps:
echo 1. Open Unity Editor
echo 2. SynLinkEditor auto-starts (check Console for startup message)
echo 3. Configure Cursor/Cline MCP settings (see SETUP.md)
echo 4. Restart Cursor
echo 5. Test: use unity_ping command!
echo.
echo Location: %~dp0build\index.js
echo.
pause
