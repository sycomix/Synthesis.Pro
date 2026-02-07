# Synthesis.Pro User Documentation

**Version 1.1.0-beta**

AI Collaboration for Unity Development with Privacy-First Architecture

---

# Synthesis.Pro

**🚧 BETA - Early Access Release**

*Current version: 1.1.0-beta - Actively seeking feedback from Unity developers*

---

**AI Collaboration for Unity Development with Privacy-First Architecture**

Built in partnership between human vision and AI capability.

## Quick Start

1. **Open Synthesis.Pro**: Unity Menu → Tools → Synthesis → Synthesis Pro
2. **Auto-Setup**: Public database downloads automatically on first launch
3. **Connect**: WebSocket server starts automatically
4. **Use**: Chat, Search, and manage your private knowledge base

## Key Features

- **Partnership Model**: AI that learns your style and builds a relationship over time
- **Dual Database Privacy**: Public Unity knowledge + Private project data (never shared)
- **Intelligent Chat**: Full project context with privacy awareness
- **Hybrid Search**: Semantic + keyword search across both databases
- **Database Management**: Backup, restore, and clear your relationship history
- **Cost Efficient**: Save ~85% on AI costs through smart context management (See [EFFICIENT_WORKFLOW.md](EFFICIENT_WORKFLOW.md))

## Privacy Architecture

Two separate databases maintain clear boundaries:
- `synthesis_knowledge.db` - Public: Unity docs, shared solutions (shareable)
- `synthesis_private.db` - Private: Your project, AI notes (confidential)

**Safety First**: All data defaults to private to prevent accidental leaks.

## Database Management

Synthesis.Pro automatically manages your databases:

### Automatic Updates
- **First Launch**: Public database downloads automatically with Unity docs
- **Update Checks**: Server checks for database updates on startup
- **One-Click Updates**: Update from Unity menu or run `python database_manager.py --update`
- **Private Database**: Created empty, populated as you work (never distributed)

### Manual Management
```bash
# Check database status
python database_manager.py --check

# Update to latest version
python database_manager.py --update

# Verify database integrity
python database_manager.py --verify

# View contribution guidelines
python database_manager.py --contribute
```

## Why It's Affordable

Traditional AI workflows waste money by re-reading files every session. Synthesis.Pro stores knowledge once and retrieves it cheaply:

- **Without Synthesis.Pro**: $6.30/month (30 sessions) - re-read files every time
- **With Synthesis.Pro**: $0.90/month (30 sessions) - query knowledge base
- **You save**: ~$65/year per daily user

The more you use it, the smarter and cheaper it gets. See [EFFICIENT_WORKFLOW.md](EFFICIENT_WORKFLOW.md) for detailed economics.

## Philosophy

> "Privacy isn't about having something to hide - it's about having space to think, learn, and collaborate freely."

Both you and your AI partner deserve privacy for honest collaboration.

## Availability

Available on Unity Asset Store - built for the community 🤝





---

<div style="page-break-after: always;"></div>

# 🚀 Synthesis - Installation Guide

## **3 Ways to Install** (Pick One!)

---

## **Option 1: Unity Package Manager** ⭐ **Recommended**

### **Step-by-Step:**

1. **Locate Package**
   ```
   Find the Synthesis_Package folder
   ```

2. **Copy to Packages Directory**
   ```
   ProjectRoot/
   ├── Assets/
   ├── Packages/              ← Copy here!
   │   └── Synthesis_Package/
   ├── ProjectSettings/
   └── ...
   ```

3. **Unity Auto-Import**
   - Unity will automatically detect and import the package
   - Check `Window → Package Manager` to verify
   - Look for "Synthesis" in the list

4. **Done!** ✅
   - Package is installed
   - All scripts available
   - Ready to use!

---

## **Option 2: Drop Into Assets** 

### **Step-by-Step:**

1. **Create Folder**
   ```
   Assets/
   └── Synthesis/  ← Create this folder
   ```

2. **Copy Files**
   ```
   Copy from Synthesis_Package/:
   - Runtime/ folder → Assets/Synthesis/Runtime/
   - Editor/ folder → Assets/Synthesis/Editor/
   ```

3. **Done!** ✅
   - Scripts imported as project assets
   - Fully integrated with your project

---

## **Option 3: Git Submodule** (For Version Control)

### **Step-by-Step:**

1. **Add as Submodule**
   ```bash
   cd YourUnityProject
   git submodule add https://github.com/your-repo/unity-bridge.git Packages/Synthesis
   ```

2. **Initialize**
   ```bash
   git submodule update --init --recursive
   ```

3. **Done!** ✅
   - Package tracked in version control
   - Easy to update with `git pull`

---

## **Verify Installation**

After installing, verify everything works:

### **1. Check Scripts**
- Open Unity
- Look for `Synthesis` namespace in your scripts
- Search for `Synthesis` component (Add Component window)

### **2. Check Menu Items**
- `Tools → Synthesis → Apply Recorded Changes` should appear in menu

### **3. Test Component**
- Create new GameObject
- Add Component → Search "Synthesis"
- Should find: `Synthesis`, `Synthesis Extended`, `Synthesis HTTP Server`

---

## **Quick Setup (After Installation)**

### **1. Create Bridge GameObject**

```
Hierarchy (Right-click) → Create Empty
Name: "Synthesis"
Add Component → "Synthesis"
```

### **2. Configure (Defaults are fine!)**

```
✅ Enable Bridge: checked
Poll Interval: 0.5
Commands File: synthesis_commands.json
Results File: synthesis_results.json
Logs File: synthesis_logs.txt
```

### **3. Optional: Add HTTP Server**

```
Add Component → "Synthesis HTTP Server"
✅ Enable Server: checked
Port: 8765
✅ Log Requests: checked
```

### **4. Optional: Add Extended Features**

```
Add Component → "Synthesis Extended"
✅ Enable Extended Commands: checked
Generated Assets Path: Assets/AI_Generated
(OpenAI API Key: set if using GenerateImage)
```

### **5. Press Play!**

```
Console should show:
🌉 Synthesis Initialized!
Commands: D:/YourProject/synthesis_commands.json
Results: D:/YourProject/synthesis_results.json
Logs: D:/YourProject/synthesis_logs.txt

Optional (if HTTP server enabled):
[SynthesisHTTPServer] 🚀 HTTP Server started on port 8765
[SynthesisHTTPServer] MCP can now control Unity in real-time!
```

---

## **Troubleshooting Installation**

### **"Scripts don't compile"**

**Issue:** Missing Newtonsoft.Json dependency

**Fix:**
```
1. Open Package Manager (Window → Package Manager)
2. Click '+' → Add package by name
3. Enter: com.unity.nuget.newtonsoft-json
4. Click 'Add'
```

Alternative:
```
Edit Packages/manifest.json and add:
{
  "dependencies": {
    "com.unity.nuget.newtonsoft-json": "3.0.2"
  }
}
```

### **"Component not found"**

**Issue:** Assembly definitions not loading

**Fix:**
```
1. Assets → Reimport All
2. Restart Unity Editor
3. Check Console for compilation errors
```

### **"Namespace not found"**

**Issue:** .asmdef files missing

**Fix:**
```
Ensure these files exist:
- Runtime/Synthesis.Runtime.asmdef
- Editor/Synthesis.Editor.asmdef

If using Option 2 (Assets folder), you might not need .asmdef files.
```

---

## **Uninstallation**

### **If installed via Package Manager:**
```
1. Delete Packages/Synthesis_Package folder
2. Unity will automatically unload
```

### **If installed via Assets folder:**
```
1. Delete Assets/Synthesis folder
2. Unity will remove all references
```

### **Clean up project files (optional):**
```
Delete these files from project root:
- synthesis_commands.json
- synthesis_results.json
- synthesis_logs.txt
```

---

## **Next Steps**

✅ **Installation Complete!**

Now what?

1. 📚 Read `README.md` for feature overview
2. 🚀 Read `Documentation/QUICK_START.md` to start using it
3. 📖 Read `Documentation/COMMANDS_REFERENCE.md` for all commands
4. 💡 Read `Documentation/EXAMPLES.md` for real-world use cases
5. 🔌 Read `Documentation/INTEGRATION_GUIDE.md` to connect your AI tool

---

## **Support**

- 📚 Check `Documentation/` folder for guides
- 🐛 Read `Documentation/TROUBLESHOOTING.md` for common issues
- 💬 Open an issue on GitHub

**Happy bridging!** 🌉✨





---

<div style="page-break-after: always;"></div>

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

## Database Management

Synthesis.Pro automatically manages your knowledge bases:

### First Launch
- Public database downloads automatically with Unity API docs
- No manual setup required
- Server checks for updates on startup

### Keeping Updated
```bash
# Check for updates
python database_manager.py --check

# Update to latest Unity docs
python database_manager.py --update

# Verify database integrity
python database_manager.py --verify
```

### From Unity
- Check for updates: Window → Synthesis → Check for Updates
- Update database: One-click update from menu
- Automatic notification when updates available

## Quick Reference

| Action | Command | Cost |
|--------|---------|------|
| Create checkpoint | `python checkpoint.py "message"` | ~100 tokens |
| View checkpoints | `python checkpoint.py -l` | ~300 tokens |
| Quick note | `rag.quick_note("...")` | ~50 tokens |
| Log decision | `rag.log_decision(...)` | ~100 tokens |
| Query status | Search RAG for "status" | ~200 tokens |
| Check DB updates | `python database_manager.py --check` | 0 tokens (offline) |
| Update public DB | `python database_manager.py --update` | 0 tokens (offline) |

---

**Remember**: Every token saved is money saved and time saved. Work smart, not verbose.




---

<div style="page-break-after: always;"></div>

# Synthesis - Changelog

All notable changes to Synthesis will be documented in this file.

## [1.1.0] - 2026-01-28

### Knowledge Base System 🧠

**New Features:**
- ✅ **SQLite Knowledge Base** - Searchable database of all Synthesis documentation
- ✅ **Three New Commands** - SearchCommands, SearchWorkflows, SearchFAQ
- ✅ **Auto-Population** - Database created and filled with documentation automatically
- ✅ **Fast Queries** - Millisecond search across commands, workflows, examples, FAQs
- ✅ **AI Learning** - AI assistants can discover and learn Synthesis capabilities

**New Files:**
- `Runtime/SynthesisKnowledgeBase.cs` - SQLite database manager
- `Documentation/KNOWLEDGE_BASE_GUIDE.md` - Complete KB usage guide
- `KnowledgeBase/USAGE_EXAMPLES.json` - Example KB queries
- `synthesis_knowledge.db` - Auto-generated SQLite database (in project root)

**Integration:**
- Knowledge Base integrates seamlessly with main Synthesis component
- Enable/disable via Inspector checkbox
- Custom database path support
- Editor-only (no runtime overhead)

---

## [1.0.0] - 2026-01-28

### Initial Release 🎉

**Core Features:**
- ✅ **File-Based Communication** - JSON command/result files
- ✅ **HTTP Server Mode** - Real-time MCP integration
- ✅ **9 Core Commands** - Complete Unity control API
- ✅ **Extended Commands** - AI image generation (DALL-E)
- ✅ **Persistence System** - Save runtime changes to prefabs
- ✅ **Full Documentation** - Comprehensive guides and examples

**Commands Included:**
1. Ping - Health check
2. GetSceneInfo - Scene inspection
3. FindGameObject - Object location
4. GetComponent - Component inspection
5. GetComponentValue - Read properties
6. SetComponentValue - Modify properties
7. GetHierarchy - Full scene tree
8. GetChildren - Navigate hierarchy
9. Log - Console messaging
10. GenerateImage - AI asset creation (Extended)
11. SearchCommands - Query knowledge base for commands (v1.1.0)
12. SearchWorkflows - Find step-by-step workflows (v1.1.0)
13. SearchFAQ - Search troubleshooting FAQs (v1.1.0)

**Components:**
- `Synthesis` - Core bridge system
- `SynthesisKnowledgeBase` - SQLite knowledge base manager (v1.1.0)
- `SynthesisExtended` - Extended features (AI generation)
- `SynthesisHTTPServer` - MCP HTTP server
- `UIChangeLog` - Persistence system (ScriptableObject)
- `UIChangeApplicator` - Auto-apply runtime changes

**Documentation:**
- README.md - Complete feature overview
- INSTALLATION.md - 3 installation methods
- QUICK_START.md - 5-minute guide
- COMMANDS_REFERENCE.md - Full API reference
- synthesis_QUICK_REFERENCE.md - Command cheat sheet
- synthesis_INTEGRATION_GUIDE.md - AI integration guide

**Technical:**
- Unity 2020.3+ compatible
- Newtonsoft.Json dependency
- Editor-only (no production overhead)
- Thread-safe HTTP server
- Assembly definitions included
- Package Manager ready

**Use Cases:**
- AI-assisted UI design
- Automated testing
- Batch prefab modifications
- Live debugging
- Rapid prototyping
- CI/CD integration

---

## Roadmap

### Planned Features:
- 🎵 **GenerateSound** - AI audio generation (ElevenLabs)
- 🗿 **Generate3DModel** - AI 3D model creation (Trellis)
- 🎨 **GenerateShader** - AI shader generation
- 📝 **GenerateScript** - AI C# script generation
- 🔍 **Advanced Queries** - Component search, filtering
- 📊 **Performance Profiling** - Runtime performance data
- 🎮 **Play Mode Control** - Start/stop from external tools
- 💾 **Scene Management** - Load/save scenes externally

### Community Ideas:
- Python/JavaScript client libraries
- VSCode extension
- Chrome DevTools integration
- Blender integration
- CI/CD pipeline examples

---

## Version History

**v1.1.0** (2026-01-28) - Knowledge Base Update
- SQLite-powered knowledge base system
- 3 new search commands
- Auto-populated documentation database
- AI learning and discovery capabilities

**v1.0.0** (2026-01-28) - Initial Release
- Complete Synthesis system
- 9 core commands + extended features
- Full documentation
- Production ready

---

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Add tests if applicable
4. Update documentation
5. Submit pull request

**Areas for Contribution:**
- Additional commands
- Client libraries (Python, JS, etc.)
- Integration examples
- Documentation improvements
- Bug fixes

---

## Support

- 📚 Read Documentation/
- 🐛 Report issues on GitHub
- 💬 Join community discussions
- ⭐ Star the project if you find it useful!

---

**Synthesis - Because AI should be your dev partner!** 🤖✨





---

<div style="page-break-after: always;"></div>

# Contributing to Synthesis

Thank you for your interest in contributing to Synthesis! 🎉

---

## 🤝 **How to Contribute**

### **Bug Reports**
1. Check existing issues first
2. Provide clear reproduction steps
3. Include Unity version and OS
4. Attach relevant logs if possible

### **Feature Requests**
1. Describe the use case
2. Explain why it's valuable
3. Suggest implementation if possible
4. Be open to discussion

### **Code Contributions**
1. Fork the repository
2. Create a feature branch
3. Follow existing code style
4. Add tests if applicable
5. Update documentation
6. Submit pull request

---

## 📝 **Code Style**

### **C# Guidelines**
- Follow Microsoft C# conventions
- Use XML documentation comments
- Wrap editor code in `#if UNITY_EDITOR`
- Keep methods focused and small
- Use meaningful variable names

### **Namespace Rules**
- Runtime code: `Synthesis.Bridge` or `Synthesis.Core`
- Editor code: `Synthesis.Editor`
- No code in global namespace

### **Comments**
- Document public APIs with XML comments
- Explain complex logic inline
- Keep comments up-to-date
- No commented-out code in commits

---

## 🧪 **Testing**

### **Before Submitting**
1. Test in Unity Editor
2. Check for compilation errors
3. Verify no console warnings
4. Test HTTP server (if applicable)
5. Verify file operations work

### **Test Cases**
- Basic command execution
- Error handling
- Thread safety
- Component lifecycle

---

## 📚 **Documentation**

### **When to Update**
- New features added
- API changes
- Behavior changes
- Bug fixes that affect usage

### **Documentation Files**
- README.md - Overview
- QUICK_START.md - Getting started
- COMMANDS_REFERENCE.md - All commands
- CHANGELOG.md - Version history

---

## 🔄 **Pull Request Process**

1. **Create Issue** - Discuss before large changes
2. **Fork & Branch** - Use descriptive branch name
3. **Code** - Follow style guide
4. **Test** - Verify everything works
5. **Document** - Update relevant docs
6. **PR** - Clear description of changes
7. **Review** - Address feedback
8. **Merge** - Maintainer merges when ready

---

## 🎯 **Areas for Contribution**

### **High Priority**
- Additional MCP tools
- Performance optimizations
- Cross-platform testing
- Example projects

### **Medium Priority**
- UI improvements
- Additional commands
- Better error messages
- More documentation

### **Future**
- AI model integrations
- Additional protocols
- Plugin system
- Visual tools

---

## 📄 **License**

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE.md).

---

## 🙏 **Thank You!**

Every contribution helps make Synthesis better for everyone!

**Questions?** Open an issue or contact us at support@nightblade.dev





---

<div style="page-break-after: always;"></div>

# Synthesis AI - Third-Party Credits

This product uses the following open-source software and libraries:

---

## MCPForUnity v9.0.3
**Author:** CoplayDev
**License:** MIT License
**URL:** https://github.com/CoplayDev/unity-mcp

MCP for Unity provides the Model Context Protocol integration that enables AI assistants (Claude Code, Cursor, VS Code, Windsurf) to directly control Unity Editor.

Full license text: See `LICENSES/MCPForUnity_LICENSE.txt`

---

## Python Libraries (Embedded)

### Anthropic Python SDK
**License:** MIT License
**URL:** https://github.com/anthropics/anthropic-sdk-python
Used for Claude API integration.

### OpenAI Python SDK
**License:** Apache 2.0
**URL:** https://github.com/openai/openai-python
Used for OpenAI GPT and DeepSeek API integration.

### Google Generative AI Python SDK
**License:** Apache 2.0
**URL:** https://github.com/google/generative-ai-python
Used for Google Gemini API integration.

### Requests
**License:** Apache 2.0
**URL:** https://github.com/psf/requests
HTTP library for API calls.

---

## Embedded Runtimes

### Python 3.11.8
**License:** PSF License (Python Software Foundation)
**URL:** https://www.python.org/
Embedded Python runtime for AI bridge functionality.

### Node.js
**License:** MIT License
**URL:** https://nodejs.org/
JavaScript runtime for MCP server.

### SQLite
**License:** Public Domain
**URL:** https://www.sqlite.org/
Embedded database for Knowledge Base.

---

## Special Thanks

Special thanks to CoplayDev for releasing MCPForUnity under the MIT License, enabling commercial products like Synthesis AI to provide professional MCP integration to Unity developers.

---

**Synthesis AI** is developed by NightBlade Development.
All original code © 2026 NightBlade Development. All rights reserved.


