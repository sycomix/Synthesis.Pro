# 🌉 Synthesis MCP Server

**Real-time AI ↔ Unity Communication via MCP Protocol**

This is the MCP (Model Context Protocol) server that enables instant communication between AI assistants (like Cursor/Cline) and Unity Editor through the Synthesis system.

---

## 🚀 Quick Start

**Run:** `setup_embedded_node.bat`

That's it! The script will:
1. Download portable Node.js
2. Install dependencies
3. Build the server
4. No installation required!

Then see [SETUP.md](SETUP.md) for Cursor/Cline configuration.

---

## 📦 What's Inside

- `src/index.ts` - MCP server implementation
- `package.json` - Dependencies and build scripts
- `tsconfig.json` - TypeScript configuration
- `setup_embedded_node.bat` - One-click setup script

---

## 🔧 Architecture

```
[Cursor/Cline] ↔ stdio ↔ [MCP Server] ↔ HTTP ↔ [Unity HTTP Server]
```

**Flow:**
1. You type in Cursor: "Move health bar to position (0, 120)"
2. Cursor sends MCP command via stdio
3. MCP server converts to Unity HTTP request
4. Unity executes command via SynLinkEditor (HTTP server)
5. Unity sends result back
6. MCP server formats response
7. You see result instantly!

**Latency:** <100ms typical

---

## 🎯 Commands Available

- `unity_ping` - Test connection
- `unity_get_scene_info` - Active scene details
- `unity_find_gameobject` - Find by name
- `unity_get_component` - Component inspection
- `unity_get_component_value` - Read field value
- `unity_set_component_value` - Modify values
- `unity_get_hierarchy` - Hierarchy tree
- `unity_get_children` - Direct children
- `unity_log` - Log to Unity Console

---

## 🛠️ Manual Build (Optional)

If you prefer to use system Node.js instead of embedded:

```bash
# Install dependencies
npm install

# Build
npm run build

# Output: build/index.js
```

---

## 📚 Documentation

Full documentation in parent folder:
- `../Documentation/UNITY_BRIDGE_INTEGRATION_GUIDE.md`
- `../Documentation/COMMANDS_REFERENCE.md`
- `../README.md`

---

## ✨ Benefits

**vs. File-Based Polling:**
- ⚡ **100x faster** - Instant responses
- 🎯 **More reliable** - No file conflicts
- 💪 **Better UX** - Natural conversation flow
- 🔄 **Real-time** - Perfect for iteration

**Perfect for:**
- UI design and testing
- Rapid prototyping
- Learning from professional assets
- AI-assisted development

---

**Part of the Synthesis Unity Bridge system** 🤖✨
