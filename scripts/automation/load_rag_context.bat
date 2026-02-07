@echo off
REM Load RAG context for Claude Code sessions
REM Run this before starting a new Claude Code session to get relevant context

cd /d "%~dp0Assets\Synthesis.Pro\Server"
python\python.exe claude_rag_bridge.py --write

echo.
echo RAG context loaded! Start your Claude Code session now.
pause
