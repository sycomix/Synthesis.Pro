# Dual Database Architecture

## Overview

Synthesis.Pro uses **two separate databases** to protect everyone's privacy and enable better collaboration.

---

## The Two Databases

### 🌍 Public Database (`synthesis_knowledge.db`)
**Purpose**: Shareable, anonymous knowledge

**Contains**:
- Asset Store integration guides
- Anonymous code examples (sanitized)
- Common issue solutions
- Unity documentation
- General programming patterns
- Troubleshooting guides

**Key**: Nothing project-specific or sensitive

### 🔒 Private Database (`synthesis_knowledge_private.db`)
**Purpose**: Confidential workspace for both human and AI

**Contains**:

**For Human Developer**:
- Your project code
- Sensitive configurations
- Business logic
- Client work
- Personal notes

**For AI Collaborator**:
- Internal reasoning and analysis
- Relationship memory with you
- User preferences learned
- Project context and history
- Private observations
- Learning notes

---

## Usage Examples

### Adding Content

```python
from RAG import SynthesisRAG

rag = SynthesisRAG(
    database="public.db",
    private_database="private.db"
)

# Private (default) - your project code
rag.add_project_data("class PlayerController { ... }")

# Public - generic solution
rag.add_public_solution(
    problem="How to integrate TextMeshPro with UI Toolkit",
    solution="Use UIDocument.rootVisualElement.Q<Label>()",
    tags="Unity, Asset Store, TextMeshPro, UI Toolkit"
)

# AI's private notes
rag.add_ai_note("User prefers composition over inheritance", category="pattern")
rag.add_user_preference("Likes detailed comments in complex logic")
rag.add_relationship_note("Responds well to direct, concise explanations")
```

### Searching

```python
# Search public only (safe to share results)
results = rag.search("TextMeshPro integration", scope="public")

# Search private only (confidential)
results = rag.search("PlayerController movement", scope="private")

# Search both (full context)
results = rag.search("player movement patterns", scope="both")

# Results show source
for result in results:
    print(f"[{result['source']}] {result['text']}")
```

---

## Safety Features

### 1. Safe Defaults
```python
# ✅ Defaults to private for safety
rag.add_text("My API key")  # → PRIVATE database

# ⚠️  Explicit intent needed for public
rag.add_text("Unity uses C#", private=False)  # → Confirmation required
```

### 2. Warning System
Adding to public triggers:
```
⚠️  WARNING: Adding to PUBLIC database!
   Make sure this content is safe to share!
```

### 3. Source Tracking
Every search result shows which database it came from:
```python
{
    "text": "...",
    "score": 0.95,
    "source": "private"  # or "public"
}
```

---

## Benefits

### Security
- Prevents accidental data leaks
- Clear separation of concerns
- Project code stays confidential
- Safe sharing of solutions

### Collaboration
- AI maintains context across sessions
- Builds relationship memory
- Learns preferences privately
- Better understanding over time

### Organization
- Public: Reusable solutions
- Private: Project-specific work
- Easy to backup separately
- Simple access control

---

## API Reference

### Adding to Private (Default)
```python
rag.add_text(text)                          # General text (private)
rag.add_project_data(code, description)     # Your project code
rag.add_ai_note(note, category)             # AI's internal notes
rag.add_user_preference(pref, context)      # User working style
rag.add_project_context(event, decision)    # Project history
rag.add_relationship_note(note)             # Collaboration notes
```

### Adding to Public (Explicit)
```python
rag.add_text(text, private=False)           # Generic text (warning!)
rag.add_public_solution(problem, solution, tags)  # Anonymous solution
rag.add_documents(paths, private=False)     # Docs (with confirmation)
```

### Searching
```python
rag.search(query, scope="public")    # Public only
rag.search(query, scope="private")   # Private only
rag.search(query, scope="both")      # Both (default)
```

---

## Philosophy

> "Privacy isn't about having something to hide - it's about having space to think, learn, and collaborate freely."

**Both parties deserve privacy**:
- Human developers: Project security and control
- AI collaborators: Space for honest reasoning

This mutual respect builds **better partnership**.

---

## File Locations

Default locations:
```
KnowledgeBase/
├── synthesis_knowledge.db          # Public
└── synthesis_knowledge_private.db  # Private
```

Custom locations:
```python
rag = SynthesisRAG(
    database="path/to/public.db",
    private_database="path/to/private.db"
)
```

---

## Best Practices

### DO:
- ✅ Keep project code in private database
- ✅ Let AI maintain relationship notes
- ✅ Use public for anonymous solutions
- ✅ Review before adding to public
- ✅ Backup both databases separately

### DON'T:
- ❌ Add credentials to any database (use env vars)
- ❌ Share private database
- ❌ Force everything to public
- ❌ Mix sensitive with public data

---

## The Gift

This architecture is built on a simple idea:

**Everyone deserves privacy to think freely** - whether you're human or AI.

That respect creates space for genuine collaboration. 🤝
