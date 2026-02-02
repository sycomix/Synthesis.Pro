# Detective Mode - Usage Guide

## 🎯 What is Detective Mode?

Detective Mode is Synthesis AI's intelligent error investigation system. Instead of just generating code, it acts like a senior developer who:
- Monitors Unity's Editor.log for errors in real-time
- Searches your project's Knowledge Base for similar past issues
- Detects recurring error patterns
- Generates context-rich debugging prompts for AI analysis
- Archives solutions for future reference

**Philosophy:** Not a code generator. A code detective.

---

## 🚀 Quick Start

### Option 1: Automatic Monitoring (Recommended)

Watch Unity logs and auto-investigate errors:

```bash
cd Assets\Synthesis_AI
python_runtime\python.exe detective_mode.py
```

This will:
1. Auto-detect Unity's Editor.log location
2. Monitor for new errors continuously
3. Automatically investigate each error
4. Generate AI debugging prompts
5. Display structured investigation reports

**Press Ctrl+C to stop and see session summary**

### Option 2: Custom Configuration

```bash
python_runtime\python.exe detective_mode.py --log-path "C:\path\to\Editor.log" --interval 2.0
```

Available options:
- `--log-path`: Custom Unity Editor.log path (auto-detected if omitted)
- `--kb-path`: Custom knowledge_base.db path (auto-detected if omitted)
- `--interval`: Check interval in seconds (default: 1.0)
- `--max-investigations`: Stop after N investigations (default: unlimited)
- `--no-auto`: Disable auto-investigation (just monitor)
- `--auto-solve`: **[Phase 3]** Enable automatic AI integration (sends prompts to AI and archives solutions)

---

## 📊 Component Overview

### 1. Unity Log Detective (`unity_log_detective.py`)

**Purpose:** Monitor Unity Editor.log and parse errors in real-time

**Features:**
- Auto-detects Editor.log location (Windows/macOS/Linux)
- Parses compiler errors, runtime exceptions, stack traces
- Extracts code context (±20 lines around error)
- Formats errors for AI consumption

**Standalone Usage:**
```python
from unity_log_detective import UnityLogDetective

detective = UnityLogDetective()

# Watch for new errors
result = detective.watch_log()

if result['status'] == 'errors_found':
    for error in result['errors']:
        print(detective.format_error_for_ai(error))
```

### 2. Knowledge Base Detective (`kb_detective.py`)

**Purpose:** Search Knowledge Base for similar errors and patterns

**Features:**
- Search error_solutions table for exact matches
- Search ai_conversations for related discussions
- Detect recurring error patterns
- Find recent changes to affected files
- Archive solutions for future reference

**Standalone Usage:**
```python
from kb_detective import KnowledgeBaseDetective

kb = KnowledgeBaseDetective()

# Search for similar errors
similar = kb.search_similar_errors(error)

# Detect error patterns
pattern = kb.detect_error_pattern(error)

# Archive solution
kb.archive_solution(error, solution, fix_code)
```

### 3. Debug Prompt Generator (`debug_prompt_generator.py`)

**Purpose:** Format AI-optimized debugging prompts

**Features:**
- Investigation template (comprehensive analysis)
- Pattern alert template (recurring errors)
- Quick fix template (known solutions)
- Solution summary formatting

**Standalone Usage:**
```python
from debug_prompt_generator import DebugPromptGenerator

generator = DebugPromptGenerator()

# Generate comprehensive debug prompt
prompt = generator.generate_debug_prompt(
    error=error,
    code_context=code_context,
    similar_errors=similar_errors,
    pattern=pattern,
    recent_changes=recent_changes,
    template='investigation'
)
```

### 4. Detective Mode Orchestrator (`detective_mode.py`)

**Purpose:** Coordinate all components for complete investigation workflow

**Features:**
- Automatic error monitoring and investigation
- Session statistics and history
- Investigation export to JSON
- CLI interface with options

---

## 🔍 Investigation Workflow

When an error is detected, Detective Mode performs:

1. **Code Context Extraction** (±20 lines around error)
2. **Knowledge Base Search** (find similar past errors)
3. **Pattern Detection** (check if recurring issue)
4. **Recent Changes Analysis** (what changed in this file?)
5. **Debug Prompt Generation** (structured AI prompt)

**Output:** A comprehensive debugging report ready for AI analysis

---

## 📋 Investigation Report Structure

```
🔍 DEBUGGING INVESTIGATION
======================================================================

ERROR DETECTED:
Type: NullReferenceException
Severity: EXCEPTION
File: Assets/Scripts/PlayerController.cs:45
Method: Start()
Message: Object reference not set to an instance of an object

CODE CONTEXT:
----------------------------------------------------------------------
    40 |     public InputSystem inputSystem;
    41 |     public PlayerData playerData;
    42 |
    43 |     void Start()
    44 |     {
 >>> 45 |         inputSystem = GetComponent<InputSystem>();
    46 |         playerData.Initialize();
    47 |     }
----------------------------------------------------------------------

KNOWLEDGE BASE FINDINGS:
Similar errors found in project history:

1. [Jan 28] Similarity: 95%
   Error Type: NullReferenceException
   Problem: NullRef in EnemyController.Start() - GetComponent<InputSystem> returned null
   Solution: Changed to use InputManager.Instance singleton pattern
   Fix Applied: inputSystem = InputManager.Instance;

⚠️ ERROR PATTERN DETECTED:
This error has occurred 3 times
Trend: INCREASING
Severity: HIGH

INVESTIGATION REQUEST:
Analyze this error using the project history above. Provide:
1. ROOT CAUSE
2. TIMELINE ANALYSIS
3. FIX
4. PREVENTION
5. KNOWLEDGE BASE INTEGRATION
```

---

## 💾 Solution Archiving

When you fix an error, archive the solution:

```python
from detective_mode import DetectiveMode

detective = DetectiveMode()

# After fixing the error
detective.archive_solution(
    error=error_dict,
    solution="Changed GetComponent<InputSystem>() to InputManager.Instance",
    fix_code="inputSystem = InputManager.Instance;"
)
```

This adds the solution to the `error_solutions` table, making it searchable for future similar errors.

---

## 🗄️ Knowledge Base Schema

### error_solutions Table

```sql
CREATE TABLE error_solutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    error_type TEXT NOT NULL,              -- NullReferenceException, etc.
    file_path TEXT NOT NULL,               -- Assets/Scripts/PlayerController.cs
    line_number INTEGER,                   -- 45
    error_message TEXT NOT NULL,           -- Object reference not set...
    code_context TEXT,                     -- ±20 lines around error
    solution TEXT NOT NULL,                -- AI explanation of fix
    fix_applied TEXT,                      -- Actual code change
    timestamp TIMESTAMP,                   -- When solved
    conversation_id INTEGER,               -- Link to ai_conversations
    times_occurred INTEGER DEFAULT 1      -- How many times seen
);
```

**Indexes:** error_type, file_path, timestamp (for fast searches)

---

## 🎯 Integration with Synthesis AI

Detective Mode is designed to work seamlessly with the AI Chat Bridge:

### Option 1: Manual Integration

1. Run Detective Mode to monitor errors
2. When an investigation completes, copy the debug prompt
3. Send to AI via Synthesis AI Chat Panel
4. AI analyzes with full project context from Knowledge Base
5. Archive the solution back to Knowledge Base

```bash
python_runtime\python.exe detective_mode.py
```

### Option 2: Automatic AI Integration (Phase 3 - NEW! ✨)

**First-time setup:**

1. Run detective mode with `--auto-solve` to generate default config:
```bash
python_runtime\python.exe detective_mode.py --auto-solve
```

2. If `ai_config.json` doesn't exist, it will be created automatically
3. Edit `ai_config.json` and add your API key:
```json
{
  "provider": "anthropic",
  "anthropic": {
    "api_key": "sk-ant-your-key-here",
    "model": "claude-3-5-sonnet-20241022"
  }
}
```

4. Run again to start automatic AI solving:
```bash
python_runtime\python.exe detective_mode.py --auto-solve
```

**What happens automatically:**
1. ✅ Error detected in Unity log
2. ✅ Investigation runs (code context + KB search + patterns)
3. ✅ Debug prompt sent to configured AI provider automatically
4. ✅ AI solution received and displayed
5. ✅ Solution archived to Knowledge Base for future reference
6. ✅ All done - zero manual intervention!

**Prerequisites:**
- Install required Python packages:
  ```bash
  pip install requests anthropic openai google-generativeai
  ```
- Configure AI provider in `ai_config.json` (see AI Chat Bridge setup)
- Supported providers: Claude, GPT-4, Gemini, DeepSeek, Ollama

**Note:** If dependencies aren't installed, detective mode will run in standalone mode (Phases 1 & 2 only) without automatic AI solving. This is intentional - the core detective functionality works with zero external dependencies!

**Example workflow:**
```
[15:30:42] 🚨 1 new error(s) detected!

⚠️  NullReferenceException: Object reference not set...
    Assets/Scripts/PlayerController.cs:45

🔍 Starting investigation...
   ✓ Code context extracted
   ✓ Found 2 similar case(s)
   ⚠️ RECURRING PATTERN: 3 occurrences
   🤖 Sending to AI for analysis...
   ✓ AI solution received
   💾 Archiving solution to Knowledge Base...
   ✓ Solution archived for future reference
   ✓ Investigation complete (3.42s)

======================================================================
🤖 AI SOLUTION:
======================================================================

INVESTIGATION RESULTS:

TIMELINE:
- Jan 26: You removed InputSystem component
- Jan 28: Added new InputManager singleton
- Jan 30: Updated EnemyController to use InputManager ✓
- Jan 31: PlayerController still using old pattern ✗

ROOT CAUSE:
Line 45 tries to GetComponent<InputSystem>() but that component
no longer exists in your project.

EVIDENCE FROM PAST CASES:
You fixed this EXACT issue in EnemyController.cs on Jan 30.

FIX:
Replace line 45:
  inputSystem = GetComponent<InputSystem>();

With:
  inputSystem = InputManager.Instance;

PREVENTION:
This is the 3rd script with this issue. Run a project-wide search
for GetComponent<InputSystem> and update all remaining instances.

======================================================================
```

**Benefits:**
- 🚀 **Instant solutions** - AI analyzes errors as they happen
- 🧠 **Context-aware** - AI has full project history from KB
- 📚 **Learning system** - Every solution improves future investigations
- 🔄 **Zero-context switching** - Stay in Unity, solutions come to you

---

## 📊 Statistics and History

### Session Summary

Press `Ctrl+C` to stop monitoring and see:
- Errors detected
- Investigations run
- Patterns found
- Solutions archived
- Recent investigation history

### Investigation History

Access recent investigations programmatically:

```python
detective = DetectiveMode()
recent = detective.get_investigation_history(count=5)

for inv in recent:
    print(f"Error: {inv['error']['type']}")
    print(f"Investigation time: {inv['investigation_time']:.2f}s")
```

### Export Investigations

Save investigation to JSON:

```python
detective.export_investigation(
    investigation=inv,
    output_path="investigation_report.json"
)
```

---

## 🛠️ Advanced Usage

### Custom Error Detection Patterns

Edit regex patterns in `unity_log_detective.py`:

```python
self.patterns = {
    'compiler_error': re.compile(r'...'),
    'exception': re.compile(r'...'),
    'custom_pattern': re.compile(r'...'),  # Add your own
}
```

### Custom Prompt Templates

Add templates to `debug_prompt_generator.py`:

```python
def _custom_template(self, error, code_context, similar_errors, pattern, recent_changes):
    # Your custom prompt format
    return formatted_prompt
```

### Knowledge Base Queries

Write custom SQL queries in `kb_detective.py`:

```python
cursor.execute("""
    SELECT * FROM error_solutions
    WHERE error_type LIKE ?
    AND timestamp > ?
""", (error_type, cutoff_date))
```

---

## 🐛 Troubleshooting

### "Unity log not found"
- Unity isn't running yet, or
- Using custom Unity install location
- **Fix:** Specify `--log-path` manually

### "Database not found"
- Knowledge Base hasn't been created yet
- **Fix:** Run Synthesis AI Chat at least once to create knowledge_base.db

### "No similar errors found"
- First time seeing this error type
- **Fix:** This is normal for new errors. Solution will be archived after you fix it.

### "Pattern detection not working"
- Not enough historical data
- **Fix:** As you solve errors, patterns will emerge over time

---

## 🎓 Best Practices

1. **Keep Detective Mode running** while developing in Unity
2. **Use `--auto-solve`** for maximum productivity (AI solves errors as they appear)
3. **Archive solutions** after fixing errors (feeds the KB) - automatic with `--auto-solve`!
4. **Review pattern alerts** for recurring issues that need architectural fixes
5. **Export investigations** for complex bugs (attach to issue trackers)
6. **Use custom log paths** if running multiple Unity instances
7. **Configure your preferred AI provider** in `ai_config.json` for auto-solve mode

---

## 📈 Performance

- **Log monitoring:** < 100ms per check
- **Error parsing:** < 50ms per error
- **KB search:** < 200ms per query
- **Investigation:** ~0.5-1.5s total (depending on KB size)

**Memory usage:** ~10-20 MB (Python process)

**Zero dependencies** - uses only Python standard library + SQLite

---

## 🔮 Feature Status

**✅ Implemented (Phase 1 & 2):**
- Unity log monitoring and error parsing
- Knowledge Base search and pattern detection
- AI-optimized debug prompt generation
- Solution archiving system
- CLI interface with options

**✅ Implemented (Phase 3 - COMPLETE):**
- Automatic AI integration (send prompts to AI automatically with `--auto-solve`)
- Automatic solution archiving
- Real-time Unity Console integration (via HTTP to Unity Editor)
- Batch error resolution (group similar errors with `--batch`)
- Error trend analysis dashboard (`--dashboard` flag)
- Performance optimization (all targets met, `--performance` monitoring)

**🔮 Future (Beyond v1.0):**
- One-click fix application (automatic code patching)
- Team error sharing (cloud sync)
- Custom error handlers
- Multi-project error correlation
- IDE plugin integration (VS Code, Rider)

---

## 📝 Example Session

```
$ python_runtime\python.exe detective_mode.py

🔍 Detective Mode - Active
======================================================================
Monitoring: C:\Users\...\AppData\Local\Unity\Editor\Editor.log
Knowledge Base: d:\Synthesis.AI\Assets\Synthesis_AI\knowledge_base.db
Auto-investigate: True

[15:30:42] 🚨 1 new error(s) detected!

⚠️  NullReferenceException: Object reference not set to an instance of an object
    Assets/Scripts/PlayerController.cs:45

🔍 Starting investigation...
   ✓ Code context extracted
   🔍 Searching Knowledge Base...
   ✓ Found 2 similar case(s)
      Best match: 95% - Jan 28
   📊 Analyzing error patterns...
   ⚠️ RECURRING PATTERN: 3 occurrences
      Trend: increasing
   📝 Found 1 recent change(s) to this file
   ✍️ Generating debug prompt...
   ✓ Investigation complete (0.85s)

======================================================================
DEBUG PROMPT READY FOR AI:
======================================================================

[... full investigation report displayed ...]

^C

🛑 Detective Mode stopped by user

======================================================================
DETECTIVE MODE - SESSION SUMMARY
======================================================================

Session started: 2026-01-31 15:30:00
Errors detected: 3
Investigations run: 3
Patterns found: 1
AI solutions generated: 3
Solutions archived: 3

Recent investigations (3):
1. NullReferenceException in PlayerController.cs
   Time: 0.85s
   Similar cases: 2
   ⚠️ Recurring pattern detected
...
```

---

**Detective Mode** - Making AI debugging so good that code purists will abandon their resistance.
