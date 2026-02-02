# 🌉 Synthesis - Quick Reference Card

**Version:** 1.0.0 | **Full Guide:** [synthesis_GUIDE.md](synthesis_GUIDE.md)

---

## ⚡ 30-Second Setup

### Runtime Bridge (Play Mode)
1. Create Empty GameObject → Add `Synthesis` component
2. Enter Play mode
3. Write commands to `synthesis_commands.json`
4. Read results from `synthesis_results.json`

### Editor Bridge (Edit Mode)
- **Auto-enabled!** No setup needed.
- Just write commands to `synthesis_commands.json`

---

## 📡 Command Template

```json
{
  "commands": [
    {
      "id": "unique_id",
      "type": "CommandType",
      "parameters": {
        "param1": "value1",
        "param2": "value2"
      }
    }
  ]
}
```

---

## 🎮 Core Commands

### Test Connection
```json
{"id": "1", "type": "Ping"}
```

### Find Object
```json
{
  "id": "2",
  "type": "FindGameObject",
  "parameters": {"name": "UICharacterHpMp"}
}
```

### Read Value
```json
{
  "id": "3",
  "type": "GetComponentValue",
  "parameters": {
    "object": "UICharacterHpMp",
    "component": "RectTransform",
    "field": "anchoredPosition"
  }
}
```

### Set Value
```json
{
  "id": "4",
  "type": "SetComponentValue",
  "parameters": {
    "object": "UICharacterHpMp",
    "component": "RectTransform",
    "field": "anchoredPosition",
    "value": {"x": 100, "y": 50},
    "record": false
  }
}
```

### Get Hierarchy
```json
{
  "id": "5",
  "type": "GetHierarchy",
  "parameters": {"object": "UI_Gameplay"}
}
```

### Get Children
```json
{
  "id": "6",
  "type": "GetChildren",
  "parameters": {"object": "UIGenericLayout"}
}
```

### Log Message
```json
{
  "id": "7",
  "type": "Log",
  "parameters": {
    "message": "Hello Unity!",
    "type": "Log"
  }
}
```

---

## 🔧 Common Value Types

### Vector2
```json
"value": {"x": 100, "y": 50}
```

### Vector3
```json
"value": {"x": 10, "y": 20, "z": 30}
```

### Color
```json
"value": {"r": 1.0, "g": 0.5, "b": 0.0, "a": 1.0}
```

### RectOffset
```json
"value": {"left": 10, "right": 10, "top": 5, "bottom": 5}
```

### Enum (as string)
```json
"value": "MiddleCenter"
```

### Primitives
```json
"value": 42          // int
"value": 3.14        // float
"value": true        // bool
"value": "text"      // string
```

---

## 💾 Persistence (Runtime → Permanent)

### Setup
1. Create: `Assets → Create → NightBlade → UI Change Log`
2. Assign to Synthesis component's `Change Log` field

### Usage
Add `"record": true` to save changes:

```json
{
  "type": "SetComponentValue",
  "parameters": {
    "object": "HealthBar",
    "component": "RectTransform",
    "field": "anchoredPosition",
    "value": {"x": 200, "y": 100},
    "record": true
  }
}
```

Exit Play mode → Changes apply automatically!

---

## 🎯 Common Patterns

### Position UI Element
```json
{
  "type": "SetComponentValue",
  "parameters": {
    "object": "HealthBar",
    "component": "RectTransform",
    "field": "anchoredPosition",
    "value": {"x": 0, "y": 120}
  }
}
```

### Resize UI Element
```json
{
  "type": "SetComponentValue",
  "parameters": {
    "object": "HealthBar",
    "component": "RectTransform",
    "field": "sizeDelta",
    "value": {"x": 400, "y": 80}
  }
}
```

### Change Color
```json
{
  "type": "SetComponentValue",
  "parameters": {
    "object": "HealthBar",
    "component": "Image",
    "field": "color",
    "value": {"r": 1.0, "g": 0.0, "b": 0.0, "a": 1.0}
  }
}
```

### Set Text
```json
{
  "type": "SetComponentValue",
  "parameters": {
    "object": "LabelHealth",
    "component": "Text",
    "field": "text",
    "value": "HP: 100/100"
  }
}
```

### Configure Grid Layout
```json
{
  "type": "SetComponentValue",
  "parameters": {
    "object": "HotbarContainer",
    "component": "GridLayoutGroup",
    "field": "cellSize",
    "value": {"x": 64, "y": 64}
  }
}
```

### Set Alignment (Enum)
```json
{
  "type": "SetComponentValue",
  "parameters": {
    "object": "HotbarContainer",
    "component": "GridLayoutGroup",
    "field": "childAlignment",
    "value": "MiddleCenter"
  }
}
```

---

## 🔍 Debugging

### Check if Bridge is Active
Look for: `synthesis_logs.txt` in project root

### View Last Result
Open: `synthesis_results.json`

### Common Issues

#### "GameObject not found"
- Check name exactly (case-sensitive)
- Use full path: `"Parent/Child/Target"`
- Verify object is active

#### "Field not found"
- Check spelling: `anchoredPosition` not `m_AnchoredPosition`
- Use `GetComponentValue` to list all available fields

#### "Type conversion failed"
- Match value format to field type
- Vector2: `{"x": 0, "y": 0}`
- Enum: Use string name

#### "Changes not persisting"
- Add `"record": true` to command
- Verify UIChangeLog asset exists and is assigned
- Check Console for applicator messages

---

## 📊 File Locations

```
ProjectRoot/
├── synthesis_commands.json   ← Write commands here
├── synthesis_results.json    ← Read results here
└── synthesis_logs.txt        ← Check activity log
```

---

## ⚡ Performance

| Metric | Value |
|--------|-------|
| Polling Interval | 0.5s (configurable) |
| Idle Overhead | ~0.1ms |
| File I/O | Async, non-blocking |
| Build Impact | None (editor-only) |

---

## 🔒 Safety

- ✅ Editor-only (disabled in builds)
- ✅ Command validation
- ✅ Error recovery (no crashes)
- ✅ Undo support (Ctrl+Z)
- ✅ Rate limiting

---

## 📚 Learn More

- **Full Guide:** [synthesis_GUIDE.md](synthesis_GUIDE.md)
- **Examples:** See guide's "Use Cases" section
- **API Reference:** See guide's "API Reference" section
- **Troubleshooting:** See guide's "Troubleshooting" section

---

## 🚀 Quick Start Example

**Goal:** Move health bar to bottom-center

**Step 1:** Write command
```json
{
  "commands": [
    {
      "id": "move_hp",
      "type": "SetComponentValue",
      "parameters": {
        "object": "UICharacterHpMp",
        "component": "RectTransform",
        "field": "anchoredPosition",
        "value": {"x": 0, "y": 120},
        "record": true
      }
    }
  ]
}
```

**Step 2:** Save file (Unity auto-detects)

**Step 3:** Check result in Unity + `synthesis_results.json`

**Step 4:** Exit Play mode → Change persists!

---

## 💡 Pro Tips

1. **Use hierarchical paths** for precision: `"UI_Gameplay/UIGenericLayout/Map"`
2. **Query before modifying**: Use `GetComponentValue` to see current state
3. **Batch commands** for efficiency: Multiple commands in one JSON file
4. **Record successful experiments**: Add `"record": true` when you like the result
5. **Check logs often**: `synthesis_logs.txt` shows all activity

---

**Need Help?** See [synthesis_GUIDE.md](synthesis_GUIDE.md) for 200+ pages of documentation!

---

🤖 **Empowering AI-Human Collaboration** | v1.0.0 | 2026-01-24

