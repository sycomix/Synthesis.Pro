# Synthesis.Pro Python Utilities

Debugging and monitoring utilities for Unity development.

## Available Utilities

### 🔍 **Detective & Debugging**
- **detective_mode.py** - Advanced debugging mode for Unity issues
- **kb_detective.py** - Knowledge base debugging and analysis
- **unity_log_detective.py** - Unity log file analysis
- **debug_prompt_generator.py** - Generate debug prompts for AI

### 📊 **Monitoring & Analytics**
- **ai_confidence_tracker.py** - Track AI confidence levels
- **error_trend_dashboard.py** - Error trend analysis and visualization
- **performance_monitor.py** - Performance tracking and profiling
- **unity_console_reporter.py** - Unity console output reporting

## ⚠️ **Status: Needs Update**

These utilities were copied from the prototype and need updating for:

1. **Dual Database Structure**
   - Update to use `SynthesisRAG` with public/private databases
   - Change database connections to new architecture
   - Use private database for sensitive data

2. **New RAG Engine**
   - Replace vanilla RAG calls with hybrid RAG
   - Update search methods
   - Use new API methods

3. **Security**
   - Ensure no API keys in code
   - Use environment variables
   - Validate inputs

## 🔧 **Usage (After Update)**

```python
from RAG import SynthesisRAG, ConversationTracker

# Initialize RAG with dual databases
rag = SynthesisRAG(
    database="public.db",
    private_database="private.db"
)

# Use utilities with updated RAG
# (specific usage will depend on utility)
```

## 📝 **TODO**

- [ ] Update all utilities for dual DB
- [ ] Test with new RAG engine
- [ ] Add examples for each utility
- [ ] Document configuration options
- [ ] Add unit tests

---

**Note**: These utilities are currently in "ported" state and need integration with the new Synthesis.Pro architecture before use.
