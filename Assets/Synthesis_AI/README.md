# ✨ Synthesis AI - AI Creative Partner for Unity (2026 Edition)

**Where human creativity and AI capability become one** 🤖🤝

**Professional commercial asset by NightBlade Development**

Synthesis AI enables real-time AI collaboration in Unity through MCP (Model Context Protocol). Work with AI assistants (Cursor, VS Code, Claude Code, Windsurf) to build, test, and refine your Unity projects with full MCP integration.

**✨ NOW WITH MCPForUnity v9.0.3!**

💼 **Commercial License** - Use in unlimited commercial projects!
🚀 **Production-Ready** - Battle-tested with 7.9 MB knowledge base
📚 **Complete Documentation** - Extensive guides + 2,497 code examples
🤝 **MCP Native** - Full protocol support, no custom setup needed
🧠 **Knowledge Base** - 86 documents, self-learning AI system
✨ **Active Support** - Professional support included
🔒 **Backup System** - Never lose your conversation history

## ⚡ **Quick Start (5 Minutes)**

### **Prerequisites**

1. **Install uv/uvx** (Python package manager):
   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
   irm https://astral.sh/uv/install.ps1 | iex
   ```

### **Installation**

1. **Import to Unity**
   - Copy the `Assets/Synthesis_AI` folder to your project
   - Unity auto-imports (includes MCPForUnity package)

2. **Open Unity**
   - Wait for: `[SynLink] 🔗 HTTP Server started on port 9765`
   - Server auto-starts in Edit Mode!

### **MCP Setup (Choose Your IDE)**

**For VS Code with Cline:**
- Already configured! MCP settings auto-updated.
- Location: `%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

**For Cursor/Claude Code/Windsurf:**
- In Unity: `Window → MCP for Unity`
- Click `Auto-Setup`
- Select your IDE
- Done!

### **Test It!**

1. Open your IDE (VS Code/Cursor/etc.)
2. Ask AI: "What's in the Unity scene?"
3. AI connects via MCP and responds!
4. All interactions saved to Knowledge Base

**No Play Mode needed** - Everything works in Edit Mode!

---

## 🎯 **What Can You Create Together?**

### **Core Features:**

#### **1. Real-Time Collaboration**
You and your AI partner work together in Unity:
```json
{"command": "GetSceneInfo", "id": "check_scene"}
→ Returns active scene name, GameObjects, components
```

#### **2. GameObject Manipulation**
AI can find and modify objects:
```json
{"command": "FindGameObject", "parameters": {"name": "Player"}}
→ Returns GameObject with ID and details

{"command": "SetComponentValue", "parameters": {
  "objectId": "123",
  "componentType": "Transform",
  "field": "position",
  "value": {"x": 10, "y": 5, "z": 0}
}}
→ Moves Player to new position
```

#### **3. Real-Time Testing**
- Modify UI during Play mode
- Test different positions/colors/values instantly
- No need to stop, edit, restart!

#### **4. Batch Operations**
- Update hundreds of GameObjects automatically
- Apply consistent styling across entire UI
- Automated testing and validation

---

## 📡 **Communication Methods**

### **Method 1: File-Based (Default)**
Simple JSON files in project root:
- `synthesis_commands.json` - AI writes commands here
- `synthesis_results.json` - Unity writes results here
- `synthesis_logs.txt` - Activity log

**Perfect for:** Cursor AI, local scripts, simple automation

### **Method 2: HTTP Server (MCP Integration)**
Real-time HTTP endpoints:
- `POST http://localhost:8765/execute` - Execute commands
- Instant responses, no polling

**Perfect for:** MCP servers, Cline, web tools, instant feedback

---

## 🔧 **Available Commands**

| Command | Description | Use Case |
|---------|-------------|----------|
| **Ping** | Check if bridge is alive | Health check |
| **GetSceneInfo** | Get active scene details | Understand scene structure |
| **FindGameObject** | Find object by name/path | Locate specific objects |
| **GetComponent** | Get component info | Inspect component properties |
| **GetComponentValue** | Read specific field/property | Get current values |
| **SetComponentValue** | Modify field/property | Change object properties |
| **GetHierarchy** | Get full scene hierarchy | See all objects |
| **GetChildren** | Get children of an object | Navigate hierarchy |
| **Log** | Send message to Unity console | Debugging |
| **SearchCommands** | Search knowledge base for commands | AI learning & discovery |
| **SearchWorkflows** | Find step-by-step workflows | Task automation |
| **SearchFAQ** | Query common questions | Troubleshooting |

### **Extended Commands** (SynthesisExtended)
- **GenerateImage** - Create 2D sprites with DALL-E
- **GenerateSound** - Create audio (planned)
- **Generate3DModel** - Create 3D models (planned)

### **Knowledge Base** (SQLite-Powered)
- **Searchable documentation** - All commands, workflows, FAQs in SQLite database
- **AI learning system** - AI assistants can discover commands and learn workflows
- **Fast queries** - Instant search across all Synthesis knowledge
- **Auto-populated** - Database created and filled automatically on first run

---

## 💡 **Real-World Examples**

### **Example 1: AI-Assisted UI Design**

**Before Synthesis:**
```
1. Stop Play mode
2. Find UI element in hierarchy
3. Change position in Inspector
4. Press Play
5. Not quite right? Repeat 1-4... 😩
```

**With Synthesis:**
```
AI: "Move the health bar 50 pixels right"
→ Instantly moves in real-time ✨
AI: "Perfect! Let's make it 20% bigger"
→ Done! 🎯
AI: "Great! Save this layout"
→ Changes persisted to prefab 💾
```

### **Example 2: Automated Testing**

```javascript
// AI can now test your game automatically!
AI: "Find the Login button"
→ Button found at position (500, 300)

AI: "What's the button's text?"
→ "LOGIN"

AI: "Change text to 'SIGN IN' and test"
→ Text updated, visually verified ✅

AI: "Apply to prefab"
→ Permanent change saved 💾
```

### **Example 3: Batch Styling**

```
AI: "Find all UI panels and set their alpha to 0.95"
→ All 47 panels updated in 0.2 seconds ⚡

AI: "Make all buttons use the primary color"
→ 23 buttons updated instantly 🎨
```

---

## 🎨 **Persistence System (Optional)**

Want to save runtime changes permanently?

1. **Create UIChangeLog Asset**
   - Right-click in Project → Create → Synthesis → UI Change Log
   - Assign to Synthesis component

2. **Make Changes in Play Mode**
   - AI modifies UI during testing
   - All changes are logged automatically

3. **Exit Play Mode**
   - Changes automatically apply to prefabs/scenes
   - No manual work needed! 🎉

---

## 🔌 **Dependencies**

**Required:**
- Unity 2020.3 or newer
- Newtonsoft.Json (automatically installed)

**Optional:**
- None! Completely self-contained

---

## 🚀 **Advanced Setup**

### **HTTP Server Mode (MCP)**

Add `SynthesisHTTPServer` component for instant communication:

```csharp
1. Add Component → SynthesisHTTPServer
2. Port: 8765 (or your preference)
3. Enable Server: ✅
4. Play!
```

Now AI can send HTTP requests:
```bash
curl -X POST http://localhost:8765/execute \
  -H "Content-Type: application/json" \
  -d '{"command":"Ping","id":"test"}'
```

---

## 📚 **Documentation**

Comprehensive guides included in `Documentation` folder:

- **QUICK_START.md** - 5-minute setup guide
- **COMMANDS_REFERENCE.md** - All available commands
- **KNOWLEDGE_BASE_GUIDE.md** - Using the SQLite knowledge base
- **INTEGRATION_GUIDE.md** - Integrate with your AI tool
- **UNITY_BRIDGE_QUICK_REFERENCE.md** - Quick command reference
- **UNITY_BRIDGE_INTEGRATION_GUIDE.md** - Deep integration guide

---

## 🎯 **Use Cases**

### **For AI-Assisted Development:**
- ✅ Rapid UI prototyping through conversation
- ✅ Live debugging without stopping Play mode
- ✅ Automated batch updates across scenes
- ✅ AI-driven game testing

### **For Automation:**
- ✅ Automated screenshot generation
- ✅ Batch prefab modifications
- ✅ Scene validation and testing
- ✅ CI/CD integration

### **For Content Creation:**
- ✅ Generate 2D assets with AI
- ✅ Create placeholder content
- ✅ Procedural asset generation
- ✅ Rapid iteration testing

---

## ⚙️ **Configuration Options**

### **Synthesis Component**

```csharp
Enable Bridge: true/false              // Turn bridge on/off
Poll Interval: 0.5 seconds              // How often to check for commands
Commands File: "synthesis_commands.json"
Results File: "synthesis_results.json"
Logs File: "synthesis_logs.txt"
Change Log: (optional UIChangeLog asset) // For persistence
```

### **SynthesisHTTPServer Component**

```csharp
Port: 8765                              // HTTP server port
Enable Server: true/false               // Turn HTTP server on/off
Log Requests: true/false                // Log all HTTP requests
```

---

## 🛡️ **Security Notes**

⚠️ **Synthesis gives external tools control over your Unity editor!**

**Best Practices:**
- ✅ **Only enable during development** (not in production builds)
- ✅ **Use localhost only** (HTTP server binds to 127.0.0.1)
- ✅ **Review AI-generated changes** before committing
- ✅ **Disable in builds** (automatically excluded from builds)

**Built-in Safety:**
- 🔒 Editor-only by default (`#if UNITY_EDITOR`)
- 🔒 No network access required (file-based mode)
- 🔒 HTTP server localhost only
- 🔒 All changes support Undo (Ctrl+Z)

---

## 🐛 **Troubleshooting**

### **"Bridge not responding"**
- ✅ Check Unity Console for `🌉 Synthesis Initialized!`
- ✅ Verify `Enable Bridge` is checked
- ✅ Check file paths exist in project root

### **"Command not executing"**
- ✅ Check `synthesis_logs.txt` for errors
- ✅ Verify JSON syntax in commands file
- ✅ Ensure GameObject/Component exists

### **"HTTP server won't start"**
- ✅ Check if port 8765 is already in use
- ✅ Try different port number
- ✅ Check Windows Firewall settings

### **"Changes not persisting"**
- ✅ Assign UIChangeLog asset to Synthesis
- ✅ Enable `Auto Apply On Exit Play Mode`
- ✅ Check Editor Console for apply messages

---

## 📦 **Package Contents**

```
Synthesis_Package/
├── Runtime/
│   ├── Synthesis.cs              // Core bridge system
│   ├── SynthesisExtended.cs      // Extended features (AI generation)
│   ├── SynthesisHTTPServer.cs    // HTTP server for MCP
│   └── UIChangeLog.cs              // Persistence system
├── Editor/
│   └── UIChangeApplicator.cs       // Applies runtime changes to prefabs
├── Documentation/
│   ├── QUICK_START.md
│   ├── COMMANDS_REFERENCE.md
│   ├── INTEGRATION_GUIDE.md
│   ├── MCP_GUIDE.md
│   ├── EXAMPLES.md
│   └── TROUBLESHOOTING.md
├── package.json                     // Unity Package Manager metadata
└── README.md                        // This file!
```

---

## 🎉 **Success Stories**

> "Designed entire UI system through conversation with Claude. What used to take 2 hours took 15 minutes!" - Game Developer

> "AI found and fixed 23 inconsistent button sizes across 8 scenes in seconds!" - UI Designer

> "No more stopping Play mode to test position tweaks. Game-changer!" - Solo Dev

---

## 🤝 **Contributing**

Synthesis is designed to be extended! Ideas for contributions:
- Additional command types
- More AI integration examples
- Language bindings (Python, JavaScript, etc.)
- MCP server implementations
- UI improvements

---

## 📄 **License**

**Commercial Asset License** - Use in unlimited projects you create!

### **✅ You Can:**
- Use in unlimited commercial & non-commercial projects
- Modify for your needs
- Sell games/apps you create with Synthesis
- Use in client work and freelance projects

### **❌ You Cannot:**
- Resell Synthesis itself
- Share with non-purchasers
- Redistribute source code

See **LICENSE.md** for complete terms.

---

## 🌟 **What's Next?**

1. ✅ Read **Documentation/QUICK_START.md**
2. ✅ Try the example commands
3. ✅ Connect your AI tool
4. ✅ Start creating! 🚀

**Synthesis: Because AI should be your dev partner, not just a chatbot!** 🤖✨

---

**Questions? Issues? Ideas?**
- Check Documentation folder
- Read TROUBLESHOOTING.md
- Open an issue on GitHub

**Happy Building!** 🎮🌉

