# Synthesis AI - 2026 Setup Guide

**Current Version:** MCPForUnity v9.0.3 + Knowledge Base System  
**Last Updated:** January 31, 2026

---

## 📋 What You Have

✅ **MCP Integration** - MCPForUnity v9.0.3 (Professional package)  
✅ **Knowledge Base** - 7.9 MB database with 86 docs, 2,497 code examples  
✅ **HTTP Server** - SynLinkEditor on port 9765 (auto-starts)  
✅ **WebSocket Server** - SynLinkWebSocket on port 9766  
✅ **AI Bridge** - Multi-provider (Anthropic, OpenAI, Ollama)  
✅ **Python Environment** - Embedded Python 3.11.8  
✅ **Backup System** - Automated database backup script  
✅ **uv/uvx** - Modern Python package management

---

## 🚀 First-Time Setup

### 1. Install uv/uvx

**Windows:**
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
irm https://astral.sh/uv/install.ps1 | iex
```

**Verify:**
```bash
uvx --version
# Should show: uvx 0.9.28
```

---

### 2. Open Unity Project

1. Open `D:\Synthesis.AI` in Unity
2. Wait for compilation
3. Check Console for: `[SynLink] 🔗 HTTP Server started on port 9765`
4. ✅ If you see this, the server is running!

---

### 3. Configure Your IDE

#### **VS Code with Cline (Already Configured!)**

MCP config is at:
```
%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json
```

Config:
```json
{
  "mcpServers": {
    "unity-mcp": {
      "command": "C:\Users\[User]\.local\bin\uvx.exe",
      "args": [
        "--from",
        "git+https://github.com/CoplayDev/unity-mcp",
        "mcp-for-unity"
      ],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

#### **Cursor / Claude Code / Windsurf**

In Unity:
1. `Window → MCP for Unity`
2. Click `Auto-Setup`
3. Select your IDE
4. Follow prompts

---

### 4. Optional: AI Chat Bridge

If you want standalone AI responses (not via IDE):

1. **Configure API Key:**
   ```bash
   # Edit: Assets/Synthesis_AI/ai_config.json
   {
     "provider": "anthropic",
     "anthropic": {
       "api_key": "sk-ant-YOUR_KEY_HERE",
       "model": "claude-3-5-sonnet-20241022"
     }
   }
   ```

2. **Start Bridge:**
   ```bash
   Assets\Synthesis_AI\start_ai_bridge.bat
   ```

---

## 🧪 Test Everything

### Quick Test Checklist:

1. **Test SynLink HTTP Server:**
   ```bash
   curl -X POST http://localhost:9765 -H "Content-Type: application/json" -d "{\"type\":\"ping\"}"
   # Should return: {"success": true, "message": "Pong! 🔗"}
   ```

2. **Test Knowledge Base:**
   ```bash
   cd KnowledgeBase
   python\python.exe nightblade_kb.py stats
   # Should show: Documents: 86, Sections: 7976, etc.
   ```

3. **Test MCP from IDE:**
   - Open VS Code/Cursor
   - Ask AI: "What GameObjects are in the Unity scene?"
   - AI should connect and respond!

---

## 📁 Important Files & Locations

### **Project Root (D:\Synthesis.AI\)**
```
D:\Synthesis.AI/
├── Assets/
│   ├── Synthesis_AI/         # Main package
│   │   ├── Runtime/           # Unity runtime scripts
│   │   ├── Editor/            # Editor scripts (SynLink)
│   │   ├── ai_chat_bridge.py  # AI bridge
│   │   └── *.md               # Documentation
│   └── MCPForUnity/           # MCP package
├── KnowledgeBase/             # Database & Python
│   ├── nightblade.db          # 7.9 MB conversation history
│   ├── nightblade_kb.db       # Metadata
│   ├── nightblade_kb.py       # Query script
│   └── python/                # Python 3.11.8
├── backup_knowledge_base.bat  # Backup script
└── CURRENT_STATUS.md          # Status report
```

### **VS Code MCP Config**
```
C:\Users\[User]\AppData\Roaming\Code\User\globalStorage\
  saoudrizwan.claude-dev\settings\cline_mcp_settings.json
```

### **uv/uvx Installation**
```
C:\Users\[User]\.local\bin\
  ├── uv.exe
  ├── uvx.exe
  └── uvw.exe
```

---

## 🔒 Backup Your Data

**CRITICAL:** Your Knowledge Base contains irreplaceable conversation history!

### Automatic Backup:
```bash
# Run anytime:
backup_knowledge_base.bat

# Creates timestamped backups in:
KnowledgeBase_Backups\
  ├── nightblade_20260131_143022.db
  └── nightblade_kb_20260131_143022.db
```

### Manual Backup:
Copy entire `KnowledgeBase/` folder to safe location (external drive, cloud storage, etc.)

---

## 🐛 Troubleshooting

### "Port 9765 already in use"
- Unity's SynLink already running (this is normal!)
- Or another Unity instance using it
- Check: `netstat -ano | findstr 9765`

### "uvx not found"
- Add to PATH: `$env:Path = "C:\Users\[User]\.local\bin;$env:Path"`
- Or reinstall uv

### "MCP not connecting"
- Check Unity Console for SynLink status
- Verify MCP config in VS Code settings
- Try `Window → MCP for Unity → Auto-Setup` in Unity

### "Knowledge Base not found"
- Verify `KnowledgeBase/nightblade.db` exists
- Run backup if missing: restore from `KnowledgeBase_Backups/`

---

## 📚 Documentation Files

- `README.md` - Main overview
- `SYNTHESIS_AI_SYSTEM_COMPLETE.md` - Complete system docs
- `KNOWLEDGE_BASE_IMPLEMENTATION.md` - KB details
- `CURRENT_STATUS.md` - Current system status
- `SETUP_2026.md` - This file!

---

## 🎯 Next Steps

1. ✅ Test MCP connection with your IDE
2. ✅ Query Knowledge Base
3. ✅ Run backup script
4. ⏳ Build website for distribution
5. ⏳ Implement cloud backup/sync
6. ⏳ Package for Asset Store

---

**Need Help?**
- Check Console logs in Unity
- Review documentation in `Assets/Synthesis_AI/`
- All conversation history saved in Knowledge Base!

**Status: PRODUCTION READY** 🚀

---

*Setup Guide - January 2026*
