# Efficient AI Workflow - Synthesis.Pro

**Goal**: Maximize productivity while minimizing context usage (time & cost)

## Core Principles

### 1. **Store, Don't Re-Read**
- Use RAG instead of re-reading files every session
- Log decisions, patterns, and status to the knowledge base
- Query RAG (~200 tokens) vs reading files (~10-30K tokens)

### 2. **Log Early, Log Often**
Use the quick helper methods:
```python
from RAG import SynthesisRAG

rag = SynthesisRAG()

# Quick one-liners
rag.quick_note("User prefers minimal comments in code")
rag.quick_note("Bug found in auth flow - needs async/await")

# Architectural decisions
rag.log_decision(
    what="Using WebSocket instead of HTTP",
    why="Need real-time bidirectional communication",
    alternatives="HTTP polling, SSE"
)

# Milestones
rag.checkpoint(
    phase="Phase 3: AI Integration",
    status="IN PROGRESS",
    next_steps="OpenAI API integration"
)

# Track what saves time/money
rag.log_efficiency_win(
    what="Checkpoint script for context restoration",
    saved="~30K tokens per context loss"
)
```

### 3. **Checkpoint at Key Moments**
Run checkpoints before/after major changes:
```bash
# Before major refactoring
python checkpoint.py "Before auth system refactor"

# After completing a phase
python checkpoint.py "Phase 3 complete - AI chat working"

# View recent checkpoints
python checkpoint.py --restore
```

### 4. **Context Recovery Pattern**
When context is lost:
1. Check last checkpoint: `python checkpoint.py -l`
2. Query RAG: Search for "project status" or "recent decisions"
3. Scan git log: `git log --oneline -5`
4. **Total cost: ~500 tokens vs 50K+ re-reading everything**

### 5. **Batch Operations**
Plan → Execute → Commit in one flow:
- Read files only when modifying them
- Use Task agents for exploration (background, don't block main context)
- Make parallel tool calls when possible

### 6. **Strategic File Reading**
```python
# ❌ Don't do this
Read entire codebase to find one function

# ✅ Do this instead
Glob for specific patterns
Grep for keywords
Read only the target file
```

## Efficiency Metrics

Track your wins in the RAG:
- Tokens saved per technique
- Time saved per workflow improvement
- Patterns that work well

## Example Session

```bash
# Start of session - restore context quickly
python checkpoint.py -l  # Check last checkpoint
# Search RAG for "current status" - get project state in ~200 tokens

# During work - log as you go
# (In Python/Unity integration)
rag.quick_note("User wants dark mode for editor window")
rag.log_decision("Using Unity UI Toolkit", "Modern, performant, official")

# End of session - create checkpoint
python checkpoint.py "Added dark mode to editor window"
git add . && git commit -m "Add dark mode support"
```

## Cost Savings - The Real Economics

### How AI Pricing Works
Claude charges per token in two categories:
- **Input tokens**: What you send TO Claude (context, files, messages) - ~$3/million
- **Output tokens**: What Claude sends back (responses) - ~$15/million

Most costs come from INPUT tokens when repeatedly sending large files for context.

### Where Money Gets Wasted (Traditional Approach)

**Every new session without RAG:**
```
Send 10 files @ 5K tokens each     = 50,000 tokens
Re-explain project context          = 10,000 tokens
Actual work/discussion              = 10,000 tokens
────────────────────────────────────────────────────
Total INPUT per session             = 70,000 tokens

Cost: 70K × $3/million = $0.21 per session
```

### How Efficiency Tools Save Money

**Session with RAG + Checkpoints:**
```
Query RAG "project status"          =    200 tokens (gets full summary)
Query RAG "recent decisions"        =    300 tokens (contextual knowledge)
Actual work/discussion              = 10,000 tokens
────────────────────────────────────────────────────
Total INPUT per session             = 10,500 tokens

Cost: 10.5K × $3/million = $0.03 per session
```

**Savings per session: $0.18 (85% reduction in input costs)**

### Real User Economics

**Casual user** (10 sessions/month):
- Without tools: $2.10/month
- With tools: $0.30/month
- **Savings: $1.80/month = $21.60/year**

**Daily developer** (30 sessions/month):
- Without tools: $6.30/month
- With tools: $0.90/month
- **Savings: $5.40/month = $64.80/year**

**Heavy user** (60 sessions/month):
- Without tools: $12.60/month
- With tools: $1.80/month
- **Savings: $10.80/month = $129.60/year**

### The Compounding Effect

The more you use the system, the more efficient it becomes:

1. **Session 1**: Add 50 files to RAG (one-time cost: ~250K tokens = $0.75)
2. **Session 2+**: Query RAG instead of re-reading files (500 tokens vs 50K tokens)
3. **Break-even**: After just 3 sessions, you've saved more than the initial indexing cost
4. **Long-term**: Every subsequent session is 85% cheaper

**Example over 6 months (30 sessions/month)**:
- Initial indexing: $0.75 (one-time)
- 180 sessions with tools: $5.40
- Total: $6.15

VS traditional approach:
- 180 sessions without tools: $37.80
- **Total savings: $31.65 over 6 months**

### How The Tools Work

1. **Store once, retrieve many**: Add a file to RAG once (~5K tokens), query it forever (~50 tokens)
2. **Incremental learning**: Each note/decision stored = one less thing to re-send later
3. **Context compression**: Checkpoint captures entire project state in ~500 tokens vs 50K+
4. **Compounding knowledge**: The longer you use it, the smarter and cheaper it gets

## The Partnership Model

This workflow treats the AI as a **partner with memory**, not a stateless tool:
- The AI learns your preferences (stored in private RAG)
- Decisions are remembered and built upon
- Patterns emerge and compound over time
- Each session is more efficient than the last

## Quick Reference

| Action | Command | Cost |
|--------|---------|------|
| Create checkpoint | `python checkpoint.py "message"` | ~100 tokens |
| View checkpoints | `python checkpoint.py -l` | ~300 tokens |
| Quick note | `rag.quick_note("...")` | ~50 tokens |
| Log decision | `rag.log_decision(...)` | ~100 tokens |
| Query status | Search RAG for "status" | ~200 tokens |

---

**Remember**: Every token saved is money saved and time saved. Work smart, not verbose.
