# Synthesis.Pro RAG Architecture

## Overview

Two RAG engines exist in this codebase:

1. **rag_engine_lite.py** (core/) - **ACTIVE** ✅
   - BM25S + sentence-transformers
   - Pure Python, no CLI dependencies
   - Fast, reliable, comfortable for AI
   - Used by all production code

2. **rag_engine.py** (deprecated/) - **DEPRECATED** ❌
   - sqlite-rag CLI-based
   - Subprocess calls
   - Kept for reference only

## Active Engine: rag_engine_lite.py

### Stack
- **BM25S**: Pure Python keyword search (500x faster)
- **sentence-transformers/all-MiniLM-L6-v2**: 80MB embedding model
- **Hybrid Search**: Reciprocal Rank Fusion
- **Direct SQLite**: No subprocess calls

### Database Architecture
- **synthesis_knowledge.db**: Public Unity knowledge (Server/database/)
- **synthesis_private.db**: Private project data (Server/database/)
- Dual database mode for privacy separation

### Why This Stack?
- No complex dependencies or CLI tools
- Reliable, predictable behavior
- Fast (~370ms queries)
- Comfortable for AI to use

## Deprecated Engine: rag_engine.py

Why deprecated:
- Subprocess calls to CLI are unreliable
- Complex dependencies (sqlite-rag, sqlite-vec)
- Slower than pure Python BM25S
- Uncomfortable for AI (CLI abstraction layer)

DO NOT import from deprecated/. Use core/rag_engine_lite.py instead.

## Migration

```python
# OLD
from rag_engine import SynthesisRAG

# NEW
from core.rag_engine_lite import SynthesisRAG
```
