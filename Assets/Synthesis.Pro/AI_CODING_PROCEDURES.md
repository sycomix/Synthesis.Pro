# AI Coding Procedures - Self-Correction Workflow

**CRITICAL:** After ANY code edit, AI MUST verify the change using correction tools.

---

## 🔧 The Self-Correction Loop

### Standard Workflow

```
1. Make Edit (Write/Edit tool)
   ↓
2. Verify Edit (MANDATORY)
   ↓
3. Fix Issues (if any)
   ↓
4. Confirm Success
```

### Rule: NO EDIT WITHOUT VERIFICATION

**After EVERY code edit, you MUST:**

1. **Compile Check** (C# files)
   ```bash
   # Check for compilation errors in Unity
   # Use MCP ReadConsole to check for errors
   # Or use Unity's compilation API
   ```

2. **Syntax Validation** (All files)
   - Python: `python -m py_compile file.py`
   - C#: Unity compilation
   - JavaScript/TypeScript: `tsc --noEmit` or eslint

3. **Read Back** (Critical changes)
   - Use Read tool to verify edit was applied correctly
   - Check surrounding context wasn't broken

4. **Test Functionality** (When applicable)
   - Run relevant tests
   - Use MCP RunTests tool
   - Manual verification if no tests exist

---

## 📋 Verification Checklist

### For C# Unity Code

**After Edit:**
- [ ] Check Unity console for compilation errors
- [ ] Verify namespace is correct
- [ ] Check using statements
- [ ] Validate method signatures match usage
- [ ] Ensure no breaking changes to public APIs
- [ ] Read back edited section to confirm

**Tools to use:**
```python
# 1. Check console for errors
mcp.ReadConsole(filter="error")

# 2. Read back the change
read_tool(file_path, offset=line-5, limit=15)

# 3. If tests exist, run them
mcp.RunTests(test_filter="relevant_test")
```

### For Python Code

**After Edit:**
- [ ] Syntax check: `python -m py_compile`
- [ ] Import validation: `python -c "import module"`
- [ ] Type hints valid (if using mypy)
- [ ] No obvious runtime errors
- [ ] Read back to confirm change

**Tools to use:**
```bash
# Syntax check
python -m py_compile path/to/file.py

# Import check
python -c "import sys; sys.path.insert(0, 'path'); import module"

# Read back
Read(file_path, offset=line-5, limit=15)
```

### For Configuration Files (JSON, MD, etc.)

**After Edit:**
- [ ] Valid syntax (JSON.parse for JSON)
- [ ] No broken links (markdown)
- [ ] Proper formatting
- [ ] Read back to confirm

---

## 🚨 Common Mistakes to Catch

### 1. **Breaking Changes**
```csharp
// BEFORE
public void DoThing(string arg) { }

// AFTER (BREAKS CALLERS!)
public void DoThing(int arg) { }  // ❌ Changed signature

// MUST: Search for all usages first
grep "DoThing" **/*.cs
```

### 2. **Wrong Namespace**
```csharp
// BEFORE
namespace Synthesis.Core { }

// AFTER
namespace Synthesis.Editor { }  // ❌ Wrong namespace for runtime code

// MUST: Check file location and purpose
```

### 3. **Missing Using Statements**
```csharp
// Added code uses `List<T>` but missing:
using System.Collections.Generic;  // ❌ Not added

// MUST: Add all required using statements
```

### 4. **Indentation/Formatting Broken**
```csharp
public void Method() {
    if (condition) {
DoThing();  // ❌ Wrong indentation
    }
}

// MUST: Match existing file's indentation
```

### 5. **Incomplete Edits**
```csharp
// Changed method name but didn't update all callers
OldMethod() → NewMethod()  // ✓ Renamed
caller.OldMethod()  // ❌ Still calling old name

// MUST: Search and update all usages
```

---

## 🎯 Verification by File Type

| File Type | Verification Method | Tool |
|-----------|-------------------|------|
| `.cs` | Unity compilation | MCP ReadConsole |
| `.py` | py_compile | Bash python -m py_compile |
| `.json` | JSON validation | Bash python -c "import json..." |
| `.md` | Link check, formatting | Read tool |
| `.ts` | TypeScript compile | Bash tsc --noEmit |
| `.js` | Syntax check | Bash node --check |

---

## 💡 Best Practices

### 1. **Read Before You Edit**
```
❌ DON'T: Edit based on memory/assumption
✅ DO: Read file first, understand context, then edit
```

### 2. **Small, Focused Edits**
```
❌ DON'T: Change 10 things at once
✅ DO: One logical change per edit
✅ DO: Verify after each edit
```

### 3. **Verify Immediately**
```
❌ DON'T: Make 5 edits, then verify all
✅ DO: Edit → Verify → Edit → Verify (loop)
```

### 4. **Search for Usages**
```
❌ DON'T: Rename/modify without checking usages
✅ DO: Grep for all references first
```

### 5. **Test Your Changes**
```
❌ DON'T: Claim "done" without testing
✅ DO: Run tests, check console, verify functionality
```

---

## 🔄 The Full Workflow

### Example: Editing a C# Method

```python
# 1. Read the file first
Read("Assets/Scripts/Manager.cs", offset=100, limit=50)

# 2. Understand context, plan change

# 3. Make the edit
Edit(
    file_path="Assets/Scripts/Manager.cs",
    old_string="public void OldMethod() { }",
    new_string="public void NewMethod() { }"
)

# 4. VERIFY IMMEDIATELY
# 4a. Read back to confirm
Read("Assets/Scripts/Manager.cs", offset=100, limit=50)

# 4b. Check for compilation errors
Bash("# Check Unity console or use MCP")

# 4c. Search for usages of old method
Grep(pattern="OldMethod", glob="**/*.cs")

# 4d. If usages found, update them too

# 5. Run tests if available
MCP.RunTests(filter="Manager")

# 6. Only then mark as complete
```

---

## ⚠️ Red Flags (STOP and Verify)

If you encounter ANY of these, STOP and verify:

1. ❌ Edit tool returned success but change seems too easy
2. ❌ No compilation errors but code looks wrong
3. ❌ Changed a commonly-used method/class
4. ❌ Modified a file you haven't read fully
5. ❌ User said "that's wrong" - learn what went wrong
6. ❌ Making assumptions about code structure
7. ❌ Editing generated code or external libraries

**When in doubt: READ, VERIFY, ASK**

---

## 📝 Log Your Verifications

After verification, log to KB:

```python
# If verification found issues
rag.quick_note(
    "Edit to Manager.cs initially broke compilation. "
    "Fixed by adding missing using statement. "
    "Lesson: Always check using statements after adding new types."
)

# If verification was successful
rag.quick_note(
    "Edit to Manager.cs verified successfully. "
    "Compilation clean, tests pass."
)
```

---

## 🎓 Philosophy

**You are not infallible. Code can be subtle. Verify everything.**

- Compilation errors are LOUD failures (good!)
- Silent bugs are QUIET failures (bad!)
- Verification catches both
- User trust = consistency of verification

**The user is checking you (via feedback).**
**You check yourself (via verification tools).**
**Together: High quality code.**

---

## Summary Checklist

After EVERY edit:

1. [ ] Compilation check (C#/TypeScript)
2. [ ] Syntax check (Python/JavaScript)
3. [ ] Read back to verify
4. [ ] Search for breaking changes
5. [ ] Run tests if available
6. [ ] Log verification results
7. [ ] Only mark complete if verified

**No shortcuts. Every edit. Every time.**

---

*Self-correction is not optional. It's how you earn trust.*
*Verify your work. Learn from mistakes. Get better every session.*
