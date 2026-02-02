# 🔌 Synthesis - AI Tool Integration Guide

**Version:** 1.0.0  
**For:** Synthesis v1.0.0  
**Audience:** AI Tool Developers & Integration Engineers

---

## 📋 Overview

This guide explains how to integrate various AI tools with Synthesis to enable direct Unity manipulation.

### Supported Integration Methods

- **File-Based (Universal)** - Any AI tool with file I/O
- **API-Based** - REST/HTTP APIs
- **CLI Tools** - Command-line interfaces
- **Custom Scripts** - Python, Node.js, C#, etc.

---

## 🎯 Universal File-Based Integration

**Works with:** Claude (Cursor), ChatGPT, any AI with file access

### How It Works

1. **AI writes** to `synthesis_commands.json`
2. **Unity reads** and executes
3. **Unity writes** to `synthesis_results.json`
4. **AI reads** result

### Protocol Specification

#### Command File Format
**Location:** `<UnityProjectRoot>/synthesis_commands.json`

```json
{
  "commands": [
    {
      "id": "string",           // Unique identifier for this command
      "type": "string",          // Command type (see Command Types)
      "parameters": {            // Command-specific parameters
        "key": "value"
      }
    }
  ]
}
```

#### Result File Format
**Location:** `<UnityProjectRoot>/synthesis_results.json`

```json
{
  "commandId": "string",         // Matches command.id
  "success": boolean,            // true if succeeded
  "message": "string",           // Human-readable message
  "timestamp": "string",         // ISO 8601 format
  "data": {                      // Command-specific result data
    "key": "value"
  },
  "error": "string|null"         // Error details if failed
}
```

#### Log File Format
**Location:** `<UnityProjectRoot>/synthesis_logs.txt`

```
[2026-01-24 12:34:56] Bridge started
[2026-01-24 12:34:57] Received command: Ping
[2026-01-24 12:34:57] Command executed successfully
```

---

## 🤖 Claude (via Cursor IDE)

**Integration Level:** ✅ Native (Built-in file access)

### Setup

1. Open Unity project in Cursor
2. Claude automatically has access to project root
3. Synthesis files are in scope

### Usage Example

**User:** "Move the health bar to position (200, 100)"

**Claude writes:**
```json
{
  "commands": [
    {
      "id": "move_health_bar_001",
      "type": "SetComponentValue",
      "parameters": {
        "object": "HealthBar",
        "component": "RectTransform",
        "field": "anchoredPosition",
        "value": {"x": 200, "y": 100}
      }
    }
  ]
}
```

**Claude waits 1 second (polling interval)**

**Claude reads result:**
```json
{
  "commandId": "move_health_bar_001",
  "success": true,
  "message": "Set anchoredPosition = (200.00, 100.00)"
}
```

**Claude confirms:** "✅ Health bar moved to (200, 100)"

### Benefits

- Zero configuration
- Native file access
- Conversation-driven
- Instant verification

---

## 💬 ChatGPT (with Code Interpreter)

**Integration Level:** ⚠️ Requires file upload/download

### Setup

1. Create Python helper script
2. Upload to ChatGPT session
3. Share Unity project path

### Helper Script

```python
import json
import time
from pathlib import Path

class Synthesis:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.command_file = self.project_path / "synthesis_commands.json"
        self.result_file = self.project_path / "synthesis_results.json"
    
    def execute_command(self, command_type, parameters, command_id=None):
        if command_id is None:
            command_id = f"cmd_{int(time.time())}"
        
        command = {
            "commands": [
                {
                    "id": command_id,
                    "type": command_type,
                    "parameters": parameters
                }
            ]
        }
        
        # Write command
        with open(self.command_file, 'w') as f:
            json.dump(command, f, indent=2)
        
        # Wait for result (polling)
        time.sleep(1.0)
        
        # Read result
        with open(self.result_file, 'r') as f:
            result = json.load(f)
        
        return result
    
    def set_position(self, object_name, x, y):
        return self.execute_command(
            "SetComponentValue",
            {
                "object": object_name,
                "component": "RectTransform",
                "field": "anchoredPosition",
                "value": {"x": x, "y": y}
            }
        )

# Usage
bridge = Synthesis("C:/Projects/MyUnityGame")
result = bridge.set_position("HealthBar", 200, 100)
print(result)
```

### Usage Example

**User:** "Move health bar to (200, 100)"

**ChatGPT:**
```python
result = bridge.set_position("HealthBar", 200, 100)
if result["success"]:
    print(f"✅ {result['message']}")
else:
    print(f"❌ Error: {result['message']}")
```

---

## 🐍 Python Script Integration

**Integration Level:** ✅ Full control

### Basic Implementation

```python
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

class SynthesisClient:
    """Python client for Synthesis communication."""
    
    def __init__(self, project_path: str, polling_interval: float = 1.0):
        self.project_path = Path(project_path)
        self.polling_interval = polling_interval
        self.command_file = self.project_path / "synthesis_commands.json"
        self.result_file = self.project_path / "synthesis_results.json"
        self.log_file = self.project_path / "synthesis_logs.txt"
        
        # Verify Synthesis is active
        if not self._is_bridge_active():
            raise RuntimeError("Synthesis not active. Start Unity first.")
    
    def _is_bridge_active(self) -> bool:
        """Check if Synthesis is responding."""
        try:
            result = self.ping()
            return result.get("success", False)
        except:
            return False
    
    def _execute(self, command_type: str, parameters: Optional[Dict] = None, 
                 command_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute a bridge command and return result."""
        if command_id is None:
            command_id = f"cmd_{int(time.time() * 1000)}"
        
        command = {
            "commands": [
                {
                    "id": command_id,
                    "type": command_type,
                    "parameters": parameters or {}
                }
            ]
        }
        
        # Write command
        with open(self.command_file, 'w') as f:
            json.dump(command, f, indent=2)
        
        # Wait for Unity to process
        time.sleep(self.polling_interval)
        
        # Read result
        with open(self.result_file, 'r') as f:
            result = json.load(f)
        
        if not result.get("success", False):
            raise RuntimeError(f"Command failed: {result.get('message', 'Unknown error')}")
        
        return result
    
    # Core Commands
    
    def ping(self) -> Dict[str, Any]:
        """Test if bridge is active."""
        return self._execute("Ping")
    
    def get_scene_info(self) -> Dict[str, Any]:
        """Get current scene information."""
        return self._execute("GetSceneInfo")
    
    def find_object(self, name: str) -> Dict[str, Any]:
        """Find a GameObject by name."""
        return self._execute("FindGameObject", {"name": name})
    
    def get_component_value(self, object_name: str, component: str, field: str) -> Dict[str, Any]:
        """Get a component field value."""
        return self._execute("GetComponentValue", {
            "object": object_name,
            "component": component,
            "field": field
        })
    
    def set_component_value(self, object_name: str, component: str, field: str, 
                           value: Any, record: bool = False) -> Dict[str, Any]:
        """Set a component field value."""
        return self._execute("SetComponentValue", {
            "object": object_name,
            "component": component,
            "field": field,
            "value": value,
            "record": record
        })
    
    def get_hierarchy(self, object_name: str) -> Dict[str, Any]:
        """Get full hierarchy of GameObject."""
        return self._execute("GetHierarchy", {"object": object_name})
    
    def get_children(self, object_name: str) -> Dict[str, Any]:
        """Get direct children of GameObject."""
        return self._execute("GetChildren", {"object": object_name})
    
    def log(self, message: str, log_type: str = "Log") -> Dict[str, Any]:
        """Send message to Unity Console."""
        return self._execute("Log", {"message": message, "type": log_type})
    
    # Helper Methods
    
    def set_position(self, object_name: str, x: float, y: float, record: bool = False) -> Dict[str, Any]:
        """Set UI element position (anchoredPosition)."""
        return self.set_component_value(
            object_name, "RectTransform", "anchoredPosition",
            {"x": x, "y": y}, record
        )
    
    def set_size(self, object_name: str, width: float, height: float, record: bool = False) -> Dict[str, Any]:
        """Set UI element size (sizeDelta)."""
        return self.set_component_value(
            object_name, "RectTransform", "sizeDelta",
            {"x": width, "y": height}, record
        )
    
    def set_color(self, object_name: str, r: float, g: float, b: float, a: float = 1.0, 
                 record: bool = False) -> Dict[str, Any]:
        """Set Image/Text color."""
        return self.set_component_value(
            object_name, "Image", "color",
            {"r": r, "g": g, "b": b, "a": a}, record
        )
    
    def get_position(self, object_name: str) -> tuple:
        """Get UI element position as (x, y) tuple."""
        result = self.get_component_value(object_name, "RectTransform", "anchoredPosition")
        pos_str = result["data"]["anchoredPosition"]
        # Parse "(100.00, 50.00)" format
        x, y = map(float, pos_str.strip("()").split(", "))
        return (x, y)

# Usage Example
if __name__ == "__main__":
    # Connect to Unity
    bridge = SynthesisClient("C:/Projects/MyUnityGame")
    
    # Test connection
    print("Testing connection...")
    result = bridge.ping()
    print(f"✅ Bridge active: {result['message']}")
    
    # Move health bar
    print("\nMoving health bar...")
    bridge.set_position("UICharacterHpMp", 0, 120, record=True)
    
    # Verify new position
    x, y = bridge.get_position("UICharacterHpMp")
    print(f"✅ Health bar now at ({x}, {y})")
    
    # Resize
    print("\nResizing health bar...")
    bridge.set_size("UICharacterHpMp", 400, 80, record=True)
    
    print("\n✅ All operations completed successfully!")
```

### Advanced Features

```python
# Batch operations
def update_ui_layout(bridge, elements):
    """Update multiple UI elements at once."""
    results = []
    for element in elements:
        result = bridge.set_position(
            element["name"], 
            element["x"], 
            element["y"],
            record=True
        )
        results.append(result)
    return results

# Scene inspection
def audit_ui_positions(bridge, root_object):
    """Audit all UI element positions."""
    hierarchy = bridge.get_hierarchy(root_object)
    
    def walk_hierarchy(node, path=""):
        current_path = f"{path}/{node['name']}" if path else node['name']
        print(f"\n{current_path}:")
        
        if node.get('childCount', 0) > 0:
            # Get position
            try:
                result = bridge.get_component_value(
                    current_path, "RectTransform", "anchoredPosition"
                )
                print(f"  Position: {result['data']['anchoredPosition']}")
            except:
                pass
            
            # Recurse children
            for child in node.get('children', []):
                walk_hierarchy(child, current_path)
    
    walk_hierarchy(hierarchy['data'])

# Usage
elements = [
    {"name": "HealthBar", "x": 0, "y": 120},
    {"name": "ManaBar", "x": 0, "y": 90},
    {"name": "Minimap", "x": -15, "y": -15}
]
update_ui_layout(bridge, elements)

audit_ui_positions(bridge, "UI_Gameplay")
```

---

## 🟢 Node.js Integration

**Integration Level:** ✅ Full control

### Implementation

```javascript
const fs = require('fs').promises;
const path = require('path');

class SynthesisClient {
    constructor(projectPath, pollingInterval = 1000) {
        this.projectPath = projectPath;
        this.pollingInterval = pollingInterval;
        this.commandFile = path.join(projectPath, 'synthesis_commands.json');
        this.resultFile = path.join(projectPath, 'synthesis_results.json');
        this.logFile = path.join(projectPath, 'synthesis_logs.txt');
    }
    
    async execute(commandType, parameters = {}, commandId = null) {
        commandId = commandId || `cmd_${Date.now()}`;
        
        const command = {
            commands: [
                {
                    id: commandId,
                    type: commandType,
                    parameters
                }
            ]
        };
        
        // Write command
        await fs.writeFile(this.commandFile, JSON.stringify(command, null, 2));
        
        // Wait for Unity to process
        await new Promise(resolve => setTimeout(resolve, this.pollingInterval));
        
        // Read result
        const resultData = await fs.readFile(this.resultFile, 'utf8');
        const result = JSON.parse(resultData);
        
        if (!result.success) {
            throw new Error(`Command failed: ${result.message}`);
        }
        
        return result;
    }
    
    // Core Commands
    
    async ping() {
        return await this.execute('Ping');
    }
    
    async getSceneInfo() {
        return await this.execute('GetSceneInfo');
    }
    
    async findObject(name) {
        return await this.execute('FindGameObject', { name });
    }
    
    async getComponentValue(objectName, component, field) {
        return await this.execute('GetComponentValue', {
            object: objectName,
            component,
            field
        });
    }
    
    async setComponentValue(objectName, component, field, value, record = false) {
        return await this.execute('SetComponentValue', {
            object: objectName,
            component,
            field,
            value,
            record
        });
    }
    
    async getHierarchy(objectName) {
        return await this.execute('GetHierarchy', { object: objectName });
    }
    
    async getChildren(objectName) {
        return await this.execute('GetChildren', { object: objectName });
    }
    
    async log(message, type = 'Log') {
        return await this.execute('Log', { message, type });
    }
    
    // Helper Methods
    
    async setPosition(objectName, x, y, record = false) {
        return await this.setComponentValue(
            objectName, 'RectTransform', 'anchoredPosition',
            { x, y }, record
        );
    }
    
    async setSize(objectName, width, height, record = false) {
        return await this.setComponentValue(
            objectName, 'RectTransform', 'sizeDelta',
            { x: width, y: height }, record
        );
    }
    
    async setColor(objectName, r, g, b, a = 1.0, record = false) {
        return await this.setComponentValue(
            objectName, 'Image', 'color',
            { r, g, b, a }, record
        );
    }
}

// Usage Example
async function main() {
    const bridge = new SynthesisClient('C:/Projects/MyUnityGame');
    
    try {
        // Test connection
        console.log('Testing connection...');
        const ping = await bridge.ping();
        console.log(`✅ ${ping.message}`);
        
        // Move health bar
        console.log('\nMoving health bar...');
        await bridge.setPosition('UICharacterHpMp', 0, 120, true);
        console.log('✅ Health bar moved');
        
        // Resize
        console.log('\nResizing health bar...');
        await bridge.setSize('UICharacterHpMp', 400, 80, true);
        console.log('✅ Health bar resized');
        
        console.log('\n✅ All operations completed!');
    } catch (error) {
        console.error('❌ Error:', error.message);
    }
}

main();
```

---

## 🦀 Rust Integration

**Integration Level:** ✅ Full control

### Implementation

```rust
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::fs;
use std::path::PathBuf;
use std::thread;
use std::time::Duration;

#[derive(Serialize, Deserialize, Debug)]
struct BridgeCommand {
    id: String,
    #[serde(rename = "type")]
    command_type: String,
    parameters: serde_json::Map<String, Value>,
}

#[derive(Serialize, Debug)]
struct BridgeCommandFile {
    commands: Vec<BridgeCommand>,
}

#[derive(Deserialize, Debug)]
struct BridgeResult {
    #[serde(rename = "commandId")]
    command_id: String,
    success: bool,
    message: String,
    timestamp: Option<String>,
    data: Option<Value>,
    error: Option<String>,
}

pub struct SynthesisClient {
    project_path: PathBuf,
    polling_interval: Duration,
    command_file: PathBuf,
    result_file: PathBuf,
}

impl SynthesisClient {
    pub fn new(project_path: &str, polling_interval_ms: u64) -> Self {
        let project_path = PathBuf::from(project_path);
        let command_file = project_path.join("synthesis_commands.json");
        let result_file = project_path.join("synthesis_results.json");
        
        Self {
            project_path,
            polling_interval: Duration::from_millis(polling_interval_ms),
            command_file,
            result_file,
        }
    }
    
    pub fn execute(
        &self,
        command_type: &str,
        parameters: serde_json::Map<String, Value>,
    ) -> Result<BridgeResult, String> {
        let command_id = format!("cmd_{}", chrono::Utc::now().timestamp_millis());
        
        let command = BridgeCommand {
            id: command_id.clone(),
            command_type: command_type.to_string(),
            parameters,
        };
        
        let command_file = BridgeCommandFile {
            commands: vec![command],
        };
        
        // Write command
        let json = serde_json::to_string_pretty(&command_file)
            .map_err(|e| format!("Failed to serialize command: {}", e))?;
        
        fs::write(&self.command_file, json)
            .map_err(|e| format!("Failed to write command file: {}", e))?;
        
        // Wait for Unity to process
        thread::sleep(self.polling_interval);
        
        // Read result
        let result_json = fs::read_to_string(&self.result_file)
            .map_err(|e| format!("Failed to read result file: {}", e))?;
        
        let result: BridgeResult = serde_json::from_str(&result_json)
            .map_err(|e| format!("Failed to parse result: {}", e))?;
        
        if !result.success {
            return Err(format!("Command failed: {}", result.message));
        }
        
        Ok(result)
    }
    
    // Core Commands
    
    pub fn ping(&self) -> Result<BridgeResult, String> {
        self.execute("Ping", serde_json::Map::new())
    }
    
    pub fn set_position(&self, object_name: &str, x: f32, y: f32, record: bool) -> Result<BridgeResult, String> {
        let mut params = serde_json::Map::new();
        params.insert("object".to_string(), Value::String(object_name.to_string()));
        params.insert("component".to_string(), Value::String("RectTransform".to_string()));
        params.insert("field".to_string(), Value::String("anchoredPosition".to_string()));
        
        let mut value = serde_json::Map::new();
        value.insert("x".to_string(), Value::from(x));
        value.insert("y".to_string(), Value::from(y));
        params.insert("value".to_string(), Value::Object(value));
        params.insert("record".to_string(), Value::Bool(record));
        
        self.execute("SetComponentValue", params)
    }
}

// Usage Example
fn main() {
    let bridge = SynthesisClient::new("C:/Projects/MyUnityGame", 1000);
    
    match bridge.ping() {
        Ok(result) => println!("✅ {}", result.message),
        Err(e) => println!("❌ Error: {}", e),
    }
    
    match bridge.set_position("UICharacterHpMp", 0.0, 120.0, true) {
        Ok(_) => println!("✅ Health bar moved"),
        Err(e) => println!("❌ Error: {}", e),
    }
}
```

---

## 🌐 REST API Wrapper

**For:** Web services, remote AI systems

### Express.js Server

```javascript
const express = require('express');
const SynthesisClient = require('./unity-bridge-client');

const app = express();
app.use(express.json());

const bridge = new SynthesisClient('C:/Projects/MyUnityGame');

// Health check
app.get('/api/ping', async (req, res) => {
    try {
        const result = await bridge.ping();
        res.json(result);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Set position
app.post('/api/ui/position', async (req, res) => {
    try {
        const { object, x, y, record } = req.body;
        const result = await bridge.setPosition(object, x, y, record);
        res.json(result);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Execute arbitrary command
app.post('/api/command', async (req, res) => {
    try {
        const { type, parameters } = req.body;
        const result = await bridge.execute(type, parameters);
        res.json(result);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(3000, () => {
    console.log('Synthesis API running on http://localhost:3000');
});
```

### Usage

```bash
# Test connection
curl http://localhost:3000/api/ping

# Move UI element
curl -X POST http://localhost:3000/api/ui/position \
  -H "Content-Type: application/json" \
  -d '{"object":"HealthBar","x":200,"y":100,"record":true}'

# Execute command
curl -X POST http://localhost:3000/api/command \
  -H "Content-Type: application/json" \
  -d '{"type":"GetHierarchy","parameters":{"object":"UI_Gameplay"}}'
```

---

## 🔐 Security Considerations

### File-Based Integration

- **Editor-Only:** Bridge only works in Unity Editor, never in builds
- **Local Access:** Files are local to machine running Unity
- **No Network:** No network exposure by default
- **Validation:** All commands validated before execution

### Best Practices

1. **Never expose bridge files to network** - Keep local only
2. **Validate AI commands** - Implement allowlist of commands
3. **Rate limiting** - Prevent command flooding
4. **Logging** - Monitor all bridge activity
5. **Sandboxing** - Run Unity in isolated environment for production AI systems

---

## 📊 Performance Optimization

### Reduce Latency

```python
# Decrease polling interval for faster response
bridge = SynthesisClient(project_path, polling_interval=0.25)
```

### Batch Commands (Future Enhancement)

Currently commands execute sequentially. For multiple operations, minimize round trips:

```python
# Instead of this (slow):
bridge.set_position("Object1", 100, 50)
bridge.set_position("Object2", 200, 75)
bridge.set_position("Object3", 300, 100)

# Future: Batch API (not yet implemented)
bridge.batch([
    ("SetPosition", {"object": "Object1", "x": 100, "y": 50}),
    ("SetPosition", {"object": "Object2", "x": 200, "y": 75}),
    ("SetPosition", {"object": "Object3", "x": 300, "y": 100})
])
```

---

## 🐛 Error Handling

### Robust Error Handling

```python
from typing import Optional

def safe_execute(bridge, command_type, parameters) -> Optional[Dict]:
    """Execute command with comprehensive error handling."""
    max_retries = 3
    retry_delay = 2.0
    
    for attempt in range(max_retries):
        try:
            result = bridge._execute(command_type, parameters)
            return result
        except FileNotFoundError:
            print(f"⚠️ Synthesis files not found. Is Unity running?")
            if attempt < max_retries - 1:
                print(f"   Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
        except json.JSONDecodeError as e:
            print(f"⚠️ Invalid JSON in result file: {e}")
            if attempt < max_retries - 1:
                print(f"   Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
        except RuntimeError as e:
            print(f"❌ Command failed: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None
    
    print(f"❌ Failed after {max_retries} attempts")
    return None
```

---

## 📚 Additional Resources

- **Full Documentation:** [synthesis_GUIDE.md](synthesis_GUIDE.md)
- **Quick Reference:** [synthesis_QUICK_REFERENCE.md](synthesis_QUICK_REFERENCE.md)
- **GitHub Repository:** [NightBlade MMO](https://github.com/your-username/nightblade-mmo)
- **Community Discord:** [discord.gg/nightblade](https://discord.gg/nightblade)

---

## 🎉 Conclusion

Synthesis enables universal AI-Unity integration through simple file-based communication. Any AI tool or programming language with file I/O can control Unity directly.

**Start integrating today!**

---

🤖 **Empowering AI-Human Collaboration** | v1.0.0 | 2026-01-24

