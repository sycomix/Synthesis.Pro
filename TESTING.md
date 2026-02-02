# Synthesis.Pro - Phase 2 Testing Guide

Quick guide to test end-to-end WebSocket communication between Unity and Python server.

## Prerequisites

- Unity project with Synthesis.Pro package
- Python 3.9+ installed
- Server dependencies installed (`pip install -r Synthesis.Pro/Server/requirements.txt`)

## Step 1: Start Python Server

```bash
cd "d:\Unity Projects\Synthesis.Pro\Synthesis.Pro\Server"
python websocket_server.py
```

**Expected Output:**
```
============================================================
🚀 Synthesis.Pro WebSocket Server
============================================================
[12:34:56] INFO - 🚀 Starting Synthesis.Pro WebSocket Server
[12:34:56] INFO - 📡 Listening on ws://localhost:8765
[12:34:56] INFO - ✅ Server ready! Waiting for Unity connections...
```

## Step 2: Setup Unity Scene

1. **Open Unity Project**
2. **Create new scene** or use existing
3. **Add SynthesisManager:**
   - Create Empty GameObject: `GameObject > Create Empty`
   - Rename to "SynthesisManager"
   - Add component: `SynthesisManager`
   - Check "Auto Create Components" (should be enabled by default)
   - Check "Auto Connect" (should be enabled by default)

## Step 3: Open Synthesis.Pro Window

1. **Open Editor Window:**
   - Menu: `Window > Synthesis.Pro`
2. **Window should show:**
   - Status: "○ DISCONNECTED" (red)
   - Connect/Disconnect buttons
   - Four tabs: Monitor, Chat, Search, Stats

## Step 4: Test Connection

### Automatic Connection (if Auto Connect enabled)

1. **Press Play in Unity**
2. **Watch Console for logs:**
   ```
   [SynthesisManager] 🎮 Synthesis Manager initialized!
   [WebSocketClient] Connecting to ws://localhost:8765...
   [WebSocketClient] ✅ Connected to Synthesis.Pro server!
   [SynthesisManager] 🌐 Connected to Synthesis.Pro server!
   ```

3. **Watch Python Server logs:**
   ```
   [12:34:56] INFO - 🔌 Unity connected: 127.0.0.1:xxxxx (total: 1)
   ```

4. **Check Synthesis.Pro Window:**
   - Status should show: "● CONNECTED" (green)

### Manual Connection (if Auto Connect disabled)

1. **Press Play in Unity**
2. **Click "Connect" button** in Synthesis.Pro window
3. **Verify logs as above**

## Step 5: Test Ping Command

1. **In Synthesis.Pro Window:**
   - Go to "Monitor" tab
   - Scroll down to "Quick Actions"
   - Click "Send Ping" button

2. **Expected Console Output:**
   ```
   [SynthesisProWindow] Ping sent
   ```

3. **Expected Python Server Output:**
   ```
   [12:34:56] INFO - 📥 Command received: ping (ID: ping_xxxxx)
   [12:34:56] INFO - ✅ Command completed: ping
   ```

4. **Check Statistics:**
   - In Monitor tab, watch "Integration" section
   - "Commands Routed" should increment
   - "Messages Sent" should increment

## Step 6: Test Chat (Optional)

1. **Go to "Chat" tab**
2. **Enter a message** in the text box
3. **Click "Send Message"**
4. **Check Console and Server logs** for communication

**Note:** Chat will work but AI response is placeholder in Phase 2 (Phase 3 will add full AI integration)

## Step 7: Test Search (Optional)

1. **Go to "Search" tab**
2. **Enter a query** (e.g., "Unity best practices")
3. **Click "Search"**
4. **Check Console and Server logs**

**Note:** Search will work if you have knowledge indexed in the database (Phase 1)

## Troubleshooting

### Connection Refused

**Problem:** `Connection failed: Connection refused`

**Solutions:**
- Ensure Python server is running (`python websocket_server.py`)
- Check port 8765 is not in use by another application
- Verify firewall isn't blocking localhost connections

### Server Not Found

**Problem:** `SynthesisManager not found in scene`

**Solution:**
- Create GameObject with SynthesisManager component
- Or click "Create SynthesisManager" button in window

### No Logs in Console

**Problem:** No connection logs appearing

**Solutions:**
- Check Unity Console is not filtered (show "Log" messages)
- Verify SynthesisManager has "Auto Connect" enabled
- Check GameObject with SynthesisManager is active in hierarchy

### RAG Errors

**Problem:** `RAG engine not available`

**Solutions:**
- Install server dependencies: `pip install -r requirements.txt`
- Check Python version is 3.9+
- Server will run without RAG but with limited features

## Success Criteria

Phase 2 is working correctly if:

- ✅ Python server starts without errors
- ✅ Unity connects to server automatically
- ✅ Synthesis.Pro window shows "CONNECTED" status
- ✅ Ping command succeeds
- ✅ Statistics increment correctly
- ✅ Both Unity and Python logs show communication

## Next Steps

After successful Phase 2 testing:
- **Phase 3:** Full AI integration with OpenAI/Claude
- **Phase 3:** Enhanced chat with AI responses
- **Phase 3:** Creative AI commands (SynLinkExtended)
- **Phase 3:** Real-time Unity manipulation via AI

---

**Need Help?** Check logs in both Unity Console and Python terminal for error details.
