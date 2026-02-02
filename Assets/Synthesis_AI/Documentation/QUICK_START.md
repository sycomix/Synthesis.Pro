# ⚡ Synthesis - 5-Minute Quick Start

Get Synthesis running in **5 minutes**!

---

## **Step 1: Install** (1 minute)

Copy `Synthesis_Package` to your project's `Packages` folder.

Unity will auto-import it. Done! ✅

---

## **Step 2: Setup** (2 minutes)

### **Create Bridge GameObject:**

1. Hierarchy → Right-click → Create Empty
2. Name it `Synthesis`
3. Add Component → `Synthesis`

### **Configure (use defaults):**
- ✅ Enable Bridge: **checked**
- Poll Interval: **0.5**
- Leave file paths as default

### **Press Play!**

Console should show:
```
🌉 Synthesis Initialized!
```

Done! ✅

---

## **Step 3: Test** (2 minutes)

###  **Test 1: Ping**

1. **Open** `synthesis_commands.json` (project root)
2. **Write:**
   ```json
   {
     "command": "Ping",
     "id": "test"
   }
   ```
3. **Save file**
4. **Wait 0.5 seconds**
5. **Open** `synthesis_results.json`
6. **See:**
   ```json
   {
     "id": "test",
     "success": true,
     "message": "pong"
   }
   ```

**It works!** 🎉

### **Test 2: Get Scene Info**

1. **Write to** `synthesis_commands.json`:
   ```json
   {
     "command": "GetSceneInfo",
     "id": "scene_check"
   }
   ```
2. **Save**
3. **Check** `synthesis_results.json`:
   ```json
   {
     "id": "scene_check",
     "success": true,
     "data": {
       "sceneName": "SampleScene",
       "gameObjects": [...],
       "rootCount": 5
     }
   }
   ```

**Perfect!** ✨

### **Test 3: Find GameObject**

1. Create a GameObject named "Player" in your scene
2. **Write:**
   ```json
   {
     "command": "FindGameObject",
     "id": "find_player",
     "parameters": {
       "name": "Player"
     }
   }
   ```
3. **Save**
4. **Check results:**
   ```json
   {
     "id": "find_player",
     "success": true,
     "data": {
       "objectId": "12345",
       "name": "Player",
       "position": {"x": 0, "y": 0, "z": 0}
     }
   }
   ```

**Awesome!** 🚀

---

## **You're Ready!**

Synthesis is now working! 🎉

### **What's Next?**

✅ Read **COMMANDS_REFERENCE.md** for all available commands  
✅ Read **EXAMPLES.md** for real-world use cases  
✅ Read **INTEGRATION_GUIDE.md** to connect your AI tool  

---

## **Common Workflows**

### **1. Modify GameObject Position**

```json
// Find object
{"command": "FindGameObject", "id": "find1", "parameters": {"name": "Player"}}
→ Get objectId from result

// Move it
{"command": "SetComponentValue", "id": "move1", "parameters": {
  "objectId": "12345",
  "componentType": "Transform",
  "field": "position",
  "value": {"x": 10, "y": 0, "z": 5}
}}
→ Player moved!
```

### **2. Change UI Text**

```json
// Find UI element
{"command": "FindGameObject", "id": "find2", "parameters": {"name": "HealthText"}}

// Change text
{"command": "SetComponentValue", "id": "text1", "parameters": {
  "objectId": "67890",
  "componentType": "TMPro.TextMeshProUGUI",
  "field": "text",
  "value": "HP: 100"
}}
→ Text updated!
```

### **3. Inspect Component**

```json
// Get Transform component
{"command": "GetComponent", "id": "inspect1", "parameters": {
  "objectId": "12345",
  "componentType": "Transform"
}}
→ Returns all Transform properties

// Get specific value
{"command": "GetComponentValue", "id": "get1", "parameters": {
  "objectId": "12345",
  "componentType": "Transform",
  "field": "position"
}}
→ Returns just the position
```

---

## **Tips**

### **⚡ Faster Testing:**
Keep both JSON files open side-by-side:
- Left: `synthesis_commands.json` (you edit this)
- Right: `synthesis_results.json` (Unity writes here)

### **🔍 Check Logs:**
Open `synthesis_logs.txt` to see all activity:
```
[10:30:45] 📥 Executing: Ping (ID: test)
[10:30:45] ✅ Success: pong
```

### **🐛 Debug Mode:**
Check Unity Console for detailed logs:
```
[Synthesis] Command received: Ping
[Synthesis] Result: {"success":true}
```

---

## **Troubleshooting**

### **"Bridge not responding"**
- ✅ Check Unity Console for "Bridge Initialized" message
- ✅ Verify "Enable Bridge" is checked
- ✅ Make sure Unity is in Play mode

### **"File not found"**
- ✅ JSON files should be in project root (same level as Assets/)
- ✅ Check file paths in Synthesis component

### **"Command not executing"**
- ✅ Verify JSON syntax is correct (use validator)
- ✅ Check `synthesis_logs.txt` for errors
- ✅ Wait at least 0.5 seconds (poll interval)

---

## **Next: Connect Your AI! 🤖**

Now that Synthesis is working, connect your AI tool:

### **Option 1: Direct File Access**
Your AI reads/writes JSON files directly.

**Example (Python):**
```python
import json
import time

# Write command
cmd = {"command": "Ping", "id": "ai_test"}
with open("synthesis_commands.json", "w") as f:
    json.dump(cmd, f)

# Wait for Unity to process
time.sleep(1)

# Read result
with open("synthesis_results.json", "r") as f:
    result = json.load(f)
print(result)  # {'id': 'ai_test', 'success': True, 'message': 'pong'}
```

### **Option 2: HTTP Server (MCP)**
Add `SynthesisHTTPServer` component for instant communication:
```
1. Add Component → Synthesis HTTP Server
2. Enable Server: ✅
3. Port: 8765
```

**Then your AI can:**
```bash
curl -X POST http://localhost:8765/execute \
  -H "Content-Type: application/json" \
  -d '{"command":"Ping","id":"test"}'
```

---

**Congratulations! You're bridging! 🌉✨**

Read more docs in the `Documentation/` folder!

