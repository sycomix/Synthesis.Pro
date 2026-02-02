# 🚀 Synthesis MCP Server - Quick Setup

## ⚡ One-Click Setup (2 Minutes)

### Step 1: Run Setup Script

**Double-click:** `setup_embedded_node.bat`

This will:
- ✅ Download portable Node.js (~30 MB)
- ✅ Install dependencies
- ✅ Build the MCP server
- ✅ No installation needed!

### Step 2: Configure Cursor/Cline

**Windows:** Edit `%APPDATA%\Roaming\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

**Mac/Linux:** `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

Add this configuration:

```json
{
  "mcpServers": {
    "synthesis": {
      "command": "node",
      "args": ["d:\\Unity Projects\\NightBlade.Game\\Synthesis_Package\\Server\\build\\index.js"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

**Note:** Adjust the path if your Synthesis package is in a different location!

### Step 3: Setup Unity

1. **Open Unity Editor** with your project
2. **Create GameObject** (or use existing one):
   - Right-click in Hierarchy → Create Empty
   - Name it "SynthesisBridge" (optional - for file-based fallback)
3. **Add Components (Optional):**
   - Add `SynLink` component (for file-based communication)
   - Add `SynLink Extended` component (for AI creative features)
   
   **Note:** The HTTP server (`SynLinkEditor`) starts automatically when Unity opens - no GameObject needed!
   
4. **Verify HTTP Server:**
   - Check Unity Console for: `[SynLink] 🔗 HTTP Server started on port 8765`
   - Enable Server: ✅ (checked)
5. **Save** scene/prefab

### Step 4: Test Connection

1. **Restart Cursor completely** (close all windows)
2. **Start Unity** (Enter Play mode or just Edit mode works too)
3. **In Cursor/Cline**, type:
   ```
   ping unity
   ```

**Expected response:**
```
✅ Pong! Unity is connected!
```

---

## 🎯 Available Commands

Once connected, you can use these Unity tools:

- `unity_ping` - Test connection
- `unity_get_scene_info` - Get active scene info
- `unity_find_gameobject` - Find GameObject by name
- `unity_get_component` - Get component data
- `unity_get_component_value` - Read specific field value
- `unity_set_component_value` - Modify component values
- `unity_get_hierarchy` - Get GameObject hierarchy tree
- `unity_get_children` - Get direct children
- `unity_log` - Log message to Unity Console

---

## 🐛 Troubleshooting

### "Cannot connect to Unity"

**Check:**
1. ✅ Unity Editor is running
2. ✅ SynLinkEditor started (check Console: `[SynLink] 🔗 HTTP Server started on port 8765`)
3. ✅ Port 8765 is not blocked by firewall
4. ✅ No connection errors in Console

### "MCP server not found"

**Check:**
1. ✅ Ran `setup_embedded_node.bat` successfully
2. ✅ `build/index.js` file exists
3. ✅ Path in cline_mcp_settings.json is correct (use full absolute path)
4. ✅ Restarted Cursor after changing settings

### "npm install failed"

**Solution:**
1. Check internet connection
2. Delete `node_modules` folder
3. Run `setup_embedded_node.bat` again

---

## 📚 Documentation

- **Full Guide:** `../Documentation/UNITY_BRIDGE_INTEGRATION_GUIDE.md`
- **Quick Reference:** `../Documentation/UNITY_BRIDGE_QUICK_REFERENCE.md`
- **Commands Reference:** `../Documentation/COMMANDS_REFERENCE.md`

---

## ✨ What This Enables

With MCP server connected, you can:

- ✅ **Inspect Unity** in natural conversation
- ✅ **Modify UI** in real-time ("move health bar to bottom center")
- ✅ **Test changes** instantly (no manual clicking)
- ✅ **Iterate rapidly** (see → adjust → repeat)
- ✅ **Learn from examples** (analyze professional UIs)

**Perfect for:**
- UI design and iteration
- Rapid prototyping
- Learning from professional assets
- AI-assisted development

---

**Ready to build amazing UIs with AI! 🎨🤖**
