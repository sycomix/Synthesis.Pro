# RAG Integration with Claude Code

## What This Does

The RAG onboarding system provides Claude with relevant context from previous work when starting a new session. Instead of starting from a blank slate, Claude gets:

- Recent work summaries
- Last errors and issues encountered
- Project status and focus areas
- Relevant past conversations

## How It Works

1. **RAG Engine**: Searches your knowledge databases (`synthesis_private.db`, `synthesis_knowledge.db`)
2. **Onboarding System**: Decides what context is relevant and helpful
3. **Bridge Script**: Updates MEMORY.md with fresh RAG context
4. **Auto Updater**: Watches for new sessions and updates context automatically
5. **Claude Code**: Loads MEMORY.md on every session (includes RAG context)

## Installation (One-Time Setup)

### Automatic Mode (Recommended)

Run once as Administrator:

```bash
install_rag_auto_updater.bat
```

This installs a background service that:
- Starts automatically when you log in to Windows
- Watches for new Claude Code sessions
- Updates RAG context automatically before each session
- Runs silently in the background

To remove it later:
```bash
uninstall_rag_auto_updater.bat
```

### Manual Mode

If you prefer manual control, run this before each session:

```bash
load_rag_context.bat
```

## What You'll See

When the RAG system has relevant context, you'll see something like:

```markdown
# RAG Context for This Session

Welcome back! You've been working on Unity. Recent focus: debugging, implementation.
Last note: "[CONSOLE:ERROR] NullReferenceException in PlayerController..."

How can I help you continue this work?
```

When there's no relevant context:

```
No RAG context available - starting with a clean slate.
```

## The "Enable, Don't Force" Philosophy

The system follows these principles:

- **Context is optional**: You can use it or ignore it
- **Non-intrusive**: Limited context per session (max 5 offers)
- **Intelligent**: Only shows context when it's likely to be helpful
- **Natural**: Presented conversationally, not as raw data

## Technical Details

- **Bridge Script**: `Assets/Synthesis.Pro/Server/claude_rag_bridge.py`
- **Memory Location**: `~/.claude/projects/d--Unity-Projects-Synthesis-Pro/memory/RAG_SESSION_CONTEXT.md`
- **RAG Onboarding**: `Assets/Synthesis.Pro/Server/rag_onboarding.py`
- **RAG Engine**: `Assets/Synthesis.Pro/RAG/rag_engine_lite.py`

## Troubleshooting

**No context showing up:**
1. Run `load_rag_context.bat` to check if RAG is working
2. Check if databases exist: `synthesis_private.db`, `synthesis_knowledge.db`
3. Verify Python runtime is set up: `Assets/Synthesis.Pro/Server/python/`

**Old/stale context:**
Run `load_rag_context.bat` before each session to get fresh context.

**Too much context:**
The system self-limits to avoid overwhelming you. If you want less, the onboarding system can be tuned in `rag_onboarding.py`.

## What's Next

This integration is Phase 1. Future enhancements:

- Automatic loading via hooks
- Context refresh during long sessions
- User feedback to improve relevance
- Integration with Unity console monitoring
