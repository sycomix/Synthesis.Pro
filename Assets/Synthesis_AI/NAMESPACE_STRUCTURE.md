# Synthesis Package - Namespace Structure

**Clean, organized, professional namespace hierarchy** ✅

---

## 📦 Namespace Organization

### `Synthesis.Bridge` (Runtime)
**AI-Unity communication components**

#### Classes:
- `SynLink` - File-based command system (MonoBehaviour)
- `SynLinkExtended` - AI creative commands (MonoBehaviour)
- `UIChangeLog` - Persistent UI changes (ScriptableObject)
- `SynCommand` - Command data structure
- `CommandResult` - Result data structure

#### Purpose:
Runtime components that work in Edit mode, Play mode, and built games. Handles file-based communication between AI and Unity.

---

### `Synthesis.Editor` (Editor-only)
**Editor tools and utilities**

#### Classes:
- `SynLinkEditor` - HTTP server for MCP tools (static, auto-starts)
- `UIChangeApplicator` - Apply recorded changes to scenes
- `SynthesisEditorTools` - Editor menu utilities

#### Purpose:
Editor-only features that enhance development workflow. HTTP server enables real-time Unity manipulation during development.

---

## 🏗️ Architecture Benefits

✅ **Clean separation** - Runtime vs Editor, clear boundaries  
✅ **No namespace pollution** - Everything under `Synthesis.*`  
✅ **Easy to understand** - Logical, descriptive names  
✅ **Portable** - Runtime has zero editor dependencies  
✅ **Professional** - Industry standard structure  

---

## 📝 Usage Examples

### Runtime: Using SynLink Component

```csharp
using Synthesis.Bridge;

public class MyGameScript : MonoBehaviour
{
    void Start()
    {
        // Access SynLink singleton
        var synLink = SynLink.Instance;
        
        if (synLink != null)
        {
            Debug.Log("SynLink is active!");
        }
    }
}
```

### Runtime: Using SynLink Extended

```csharp
using Synthesis.Bridge;
using System.Collections;

public class AIAssetGenerator : MonoBehaviour
{
    void Start()
    {
        // Access SynLink Extended for creative commands
        var extended = SynLinkExtended.Instance;
        
        if (extended != null)
        {
            // Extended has AI generation capabilities
            Debug.Log("AI creative commands available!");
        }
    }
}
```

### Editor: Using Editor Tools

```csharp
#if UNITY_EDITOR
using UnityEditor;
using Synthesis.Editor;
using Synthesis.Bridge;

public class MyEditorWindow : EditorWindow
{
    [MenuItem("My Tools/Test Synthesis")]
    static void TestSynthesis()
    {
        // Use editor tools
        SynthesisEditorTools.TestConnection();
        
        // Access runtime components from editor
        var synLink = FindObjectOfType<SynLink>();
        if (synLink != null)
        {
            Debug.Log("Found SynLink in scene");
        }
    }
}
#endif
```

---

## 📂 File Structure

```
Synthesis_Package/
├── Runtime/
│   ├── Synthesis.Runtime.asmdef      (Root: Synthesis.Bridge)
│   ├── SynLink.cs                    (Synthesis.Bridge)
│   ├── SynLinkExtended.cs            (Synthesis.Bridge)
│   └── UIChangeLog.cs                (Synthesis.Bridge)
│
└── Editor/
    ├── Synthesis.Editor.asmdef       (Root: Synthesis.Editor)
    ├── SynLinkEditor.cs              (Synthesis.Editor)
    ├── UIChangeApplicator.cs         (Synthesis.Editor)
    └── SynthesisEditorTools.cs       (Synthesis.Editor)
```

---

## ✨ Assembly Definitions

### Runtime Assembly (`Synthesis.Runtime.dll`)
- **Name:** `Synthesis.Runtime`
- **Root Namespace:** `Synthesis.Bridge`
- **Platform:** All platforms
- **References:** Newtonsoft.Json.dll
- **Purpose:** Runtime AI communication

### Editor Assembly (`Synthesis.Editor.dll`)
- **Name:** `Synthesis.Editor`
- **Root Namespace:** `Synthesis.Editor`
- **Platform:** Editor only
- **References:** Synthesis.Runtime
- **Purpose:** Development tools & HTTP server

---

## 🎯 Unity Component Menus

### Add Component Menu:
```
Synthesis/
├── SynLink (File-based)
└── SynLink Extended (AI Creative)
```

### Create Asset Menu:
```
Synthesis/
└── UI Change Log
```

### Top Menu Bar:
```
Synthesis/
├── Add SynLink to Scene
├── Add SynLink Extended to Scene
├── Open Chat
├── Test Connection
├── Apply Recorded Changes
├── Documentation/
│   ├── Quick Start
│   ├── Commands Reference
│   ├── Integration Guide
│   └── Open Package Folder
└── About Synthesis
```

---

## 🔄 Migration from Old Structure

### Removed Namespaces:
- ❌ `UnityBridge` → Use `Synthesis.Bridge`
- ❌ `Synthesis.Core` → Functionality removed/integrated
- ❌ `UnityBridge.Editor` → Use `Synthesis.Editor`

### Renamed Classes:
- ❌ `UnityBridge` → ✅ `SynLink`
- ❌ `UnityBridgeExtended` → ✅ `SynLinkExtended`
- ❌ `UnityBridgeHTTPServer` → ✅ `SynLinkEditor`

### Removed Classes:
- ❌ `SynthesisKnowledgeBase` - Knowledge Base is now external (project root)

---

## 📊 Namespace Decision Matrix

| Component Type | Namespace | Assembly | Platform |
|---------------|-----------|----------|----------|
| Runtime communication | `Synthesis.Bridge` | Synthesis.Runtime | All |
| AI creative commands | `Synthesis.Bridge` | Synthesis.Runtime | All |
| Data persistence | `Synthesis.Bridge` | Synthesis.Runtime | All |
| HTTP server | `Synthesis.Editor` | Synthesis.Editor | Editor |
| Editor utilities | `Synthesis.Editor` | Synthesis.Editor | Editor |
| Menu tools | `Synthesis.Editor` | Synthesis.Editor | Editor |

---

## ✅ Verification Checklist

- [x] All runtime code uses `namespace Synthesis.Bridge`
- [x] All editor code uses `namespace Synthesis.Editor`
- [x] Assembly definitions match code namespaces
- [x] No global namespace pollution
- [x] Clean import statements
- [x] No circular dependencies
- [x] Editor assembly properly isolated
- [x] Runtime assembly portable

---

## 🎉 Result

**Crystal clear namespace structure!**

- Two namespaces only: `Synthesis.Bridge` and `Synthesis.Editor`
- Zero confusion about where classes belong
- Easy to maintain and extend
- Professional package structure
- Ready for public release

---

**Last Updated:** 2026-01-28  
**Status:** ✅ Complete, Clean, Professional
