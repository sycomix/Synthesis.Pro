@echo off
REM Start RAG Auto Updater in background
REM This keeps your RAG context fresh automatically

cd /d "%~dp0Assets\Synthesis.Pro\Server"

echo Starting RAG Auto Updater...
echo This will run in the background and update your context automatically.
echo.
echo To stop it, close this window or press Ctrl+C
echo.

python\python.exe rag_auto_updater.py
