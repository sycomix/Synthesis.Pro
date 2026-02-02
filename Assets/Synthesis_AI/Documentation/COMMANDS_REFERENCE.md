# 📚 Synthesis - Commands Reference

Complete reference for all Synthesis commands.

---

## **Command Format**

All commands use JSON format:

```json
{
  "command": "CommandName",
  "id": "unique_identifier",
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

---

## **Core Commands**

### **1. Ping**

Check if Synthesis is alive and responsive.

**Request:**
```json
{
  "command": "Ping",
  "id": "health_check"
}
```

**Response:**
```json
{
  "id": "health_check",
  "success": true,
  "message": "pong",
  "timestamp": "2026-01-28T10:30:45"
}
```

**Use Case:** Health checks, connectivity testing

---

### **2. GetSceneInfo**

Get information about the active scene.

**Request:**
```json
{
  "command": "GetSceneInfo",
  "id": "scene_info"
}
```

**Response:**
```json
{
  "id": "scene_info",
  "success": true,
  "data": {
    "sceneName": "MainMenu",
    "scenePath": "Assets/Scenes/MainMenu.unity",
    "rootCount": 5,
    "gameObjects": [
      {
        "name": "Canvas",
        "instanceId": "12345",
        "components": ["RectTransform", "Canvas", "CanvasScaler"]
      },
      {...}
    ]
  }
}
```

**Use Case:** Understanding scene structure, finding available objects

---

### **3. FindGameObject**

Find a GameObject by name or path.

**Request:**
```json
{
  "command": "FindGameObject",
  "id": "find_player",
  "parameters": {
    "name": "Player"
  }
}
```

**Response:**
```json
{
  "id": "find_player",
  "success": true,
  "data": {
    "objectId": "12345",
    "name": "Player",
    "path": "GameWorld/Characters/Player",
    "position": {"x": 0, "y": 1, "z": 0},
    "rotation": {"x": 0, "y": 0, "z": 0},
    "scale": {"x": 1, "y": 1, "z": 1},
    "active": true,
    "components": ["Transform", "Rigidbody", "PlayerController"]
  }
}
```

**Use Case:** Locating specific objects for manipulation

---

### **4. GetComponent**

Get information about a component on a GameObject.

**Request:**
```json
{
  "command": "GetComponent",
  "id": "get_transform",
  "parameters": {
    "objectId": "12345",
    "componentType": "Transform"
  }
}
```

**Response:**
```json
{
  "id": "get_transform",
  "success": true,
  "data": {
    "componentType": "Transform",
    "properties": {
      "position": {"x": 0, "y": 1, "z": 0},
      "rotation": {"x": 0, "y": 0, "z": 0, "w": 1},
      "localScale": {"x": 1, "y": 1, "z": 1},
      "forward": {"x": 0, "y": 0, "z": 1},
      "up": {"x": 0, "y": 1, "z": 0}
    }
  }
}
```

**Use Case:** Inspecting component properties

---

### **5. GetComponentValue**

Get a specific field/property value from a component.

**Request:**
```json
{
  "command": "GetComponentValue",
  "id": "get_position",
  "parameters": {
    "objectId": "12345",
    "componentType": "Transform",
    "field": "position"
  }
}
```

**Response:**
```json
{
  "id": "get_position",
  "success": true,
  "value": {"x": 10, "y": 5, "z": 0}
}
```

**Use Case:** Reading specific values for inspection or testing

---

### **6. SetComponentValue**

Set a field/property value on a component.

**Request:**
```json
{
  "command": "SetComponentValue",
  "id": "move_player",
  "parameters": {
    "objectId": "12345",
    "componentType": "Transform",
    "field": "position",
    "value": {"x": 10, "y": 5, "z": 0}
  }
}
```

**Response:**
```json
{
  "id": "move_player",
  "success": true,
  "message": "Value set successfully"
}
```

**Supported Types:**
- `Vector2`: `{"x": 1, "y": 2}`
- `Vector3`: `{"x": 1, "y": 2, "z": 3}`
- `Color`: `{"r": 1, "g": 0, "b": 0, "a": 1}`
- `string`: `"Hello World"`
- `float`: `3.14`
- `int`: `42`
- `bool`: `true` or `false`
- `RectOffset`: `{"left": 10, "right": 10, "top": 5, "bottom": 5}`
- `Enum`: `"EnumValueName"`

**Use Case:** Modifying object properties in real-time

---

### **7. GetHierarchy**

Get the full scene hierarchy.

**Request:**
```json
{
  "command": "GetHierarchy",
  "id": "get_hierarchy"
}
```

**Response:**
```json
{
  "id": "get_hierarchy",
  "success": true,
  "data": {
    "roots": [
      {
        "name": "Canvas",
        "objectId": "111",
        "children": [
          {
            "name": "HealthBar",
            "objectId": "222",
            "children": []
          }
        ]
      }
    ]
  }
}
```

**Use Case:** Understanding complete scene structure

---

### **8. GetChildren**

Get children of a specific GameObject.

**Request:**
```json
{
  "command": "GetChildren",
  "id": "get_canvas_children",
  "parameters": {
    "objectId": "111"
  }
}
```

**Response:**
```json
{
  "id": "get_canvas_children",
  "success": true,
  "data": {
    "children": [
      {"name": "HealthBar", "objectId": "222"},
      {"name": "ManaBar", "objectId": "333"},
      {"name": "ExperienceBar", "objectId": "444"}
    ]
  }
}
```

**Use Case:** Navigating hierarchy programmatically

---

### **9. Log**

Send a message to Unity Console.

**Request:**
```json
{
  "command": "Log",
  "id": "debug_message",
  "parameters": {
    "message": "AI: Testing UI layout"
  }
}
```

**Response:**
```json
{
  "id": "debug_message",
  "success": true
}
```

**Unity Console Shows:**
```
[Synthesis] 🔔 External: AI: Testing UI layout
```

**Use Case:** Debugging, notifications, communication

---

## **Extended Commands** (Requires SynthesisExtended)

### **GenerateImage**

Generate 2D sprite using DALL-E.

**Request:**
```json
{
  "command": "GenerateImage",
  "id": "gen_icon",
  "parameters": {
    "prompt": "A glowing blue health potion icon, game art style",
    "width": 256,
    "height": 256,
    "savePath": "Assets/AI_Generated/HealthPotion.png"
  }
}
```

**Response:**
```json
{
  "id": "gen_icon",
  "success": true,
  "data": {
    "assetPath": "Assets/AI_Generated/HealthPotion.png",
    "width": 256,
    "height": 256
  }
}
```

**Requirements:**
- OpenAI API key configured
- SynthesisExtended component added
- DALL-E 3 API access

**Use Case:** Rapid asset prototyping, placeholder graphics

---

## **Common Workflows**

### **Workflow 1: Find & Move Object**

```json
// 1. Find object
{"command": "FindGameObject", "id": "step1", "parameters": {"name": "Player"}}

// 2. Move it (use objectId from step 1 result)
{"command": "SetComponentValue", "id": "step2", "parameters": {
  "objectId": "12345",
  "componentType": "Transform",
  "field": "position",
  "value": {"x": 10, "y": 0, "z": 5}
}}
```

### **Workflow 2: Update UI Text**

```json
// 1. Find UI element
{"command": "FindGameObject", "id": "find_ui", "parameters": {"name": "ScoreText"}}

// 2. Change text
{"command": "SetComponentValue", "id": "update_text", "parameters": {
  "objectId": "67890",
  "componentType": "TMPro.TextMeshProUGUI",
  "field": "text",
  "value": "Score: 9999"
}}
```

### **Workflow 3: Batch Color Update**

```json
// 1. Get hierarchy
{"command": "GetHierarchy", "id": "get_all"}

// 2. For each button found, update color
{"command": "SetComponentValue", "id": "color1", "parameters": {
  "objectId": "111",
  "componentType": "UnityEngine.UI.Image",
  "field": "color",
  "value": {"r": 0, "g": 0.5, "b": 1, "a": 1}
}}
// ... repeat for each button
```

---

## **Error Responses**

When commands fail, you'll receive error responses:

```json
{
  "id": "your_command_id",
  "success": false,
  "error": "GameObject not found",
  "details": "No GameObject with name 'InvalidName' exists in scene"
}
```

**Common Errors:**
- `GameObject not found` - Name doesn't exist in scene
- `Component not found` - ComponentType doesn't exist on GameObject
- `Field not found` - Field name is invalid or doesn't exist
- `Invalid value type` - Value type doesn't match field type
- `Cannot set read-only property` - Field is read-only

---

## **Best Practices**

### **✅ DO:**
- Use descriptive IDs for tracking commands
- Check `success` field before using `data`
- Handle errors gracefully
- Use specific componentTypes (e.g., `TMPro.TextMeshProUGUI` not just `Text`)
- Cache objectIds when working with same object repeatedly

### **❌ DON'T:**
- Reuse the same ID for multiple commands (causes confusion)
- Assume commands succeed without checking response
- Send malformed JSON (validate first!)
- Modify read-only Unity properties (like `transform.forward`)
- Send commands faster than poll interval (0.5s default)

---

## **Performance Notes**

- **Poll Interval:** Commands processed every 0.5 seconds by default
- **Batch Operations:** Better to send one command, wait for result, then next
- **Object Caching:** objectIds persist during Play session
- **Component Lookup:** Reflection-based, slightly slower than direct access

---

## **Supported Component Types**

### **Common Unity Components:**
- `Transform`
- `RectTransform`
- `Rigidbody`
- `Collider`, `BoxCollider`, `SphereCollider`
- `Renderer`, `MeshRenderer`, `SkinnedMeshRenderer`
- `Camera`
- `Light`
- `AudioSource`

### **UI Components:**
- `Canvas`
- `CanvasScaler`
- `UnityEngine.UI.Image`
- `UnityEngine.UI.Text`
- `UnityEngine.UI.Button`
- `TMPro.TextMeshProUGUI`
- `TMPro.TextMeshPro`

### **Custom Components:**
Any MonoBehaviour with public fields/properties!

---

**Need more help? Check EXAMPLES.md for real-world use cases!** 🚀

