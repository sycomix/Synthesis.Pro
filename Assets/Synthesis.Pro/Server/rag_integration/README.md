# RAG Integration Layer

How the RAG engine integrates with the WebSocket server.

## Components

- **rag_onboarding.py**: Coordinates context systems for natural RAG usage
- **claude_rag_bridge.py**: Claude Code-specific integration
- **rag_auto_updater.py**: Automatic database updates for Claude

## Architecture

Unity → WebSocket → rag_integration → RAG Engine (../RAG/core/)
                          ↓
                   Context Systems (../context_systems/)

See [RAG Engine Documentation](../../RAG/docs/ARCHITECTURE.md) for engine details.
