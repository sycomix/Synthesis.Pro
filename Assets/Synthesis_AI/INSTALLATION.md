# 🚀 Synthesis - Installation Guide

## **3 Ways to Install** (Pick One!)

---

## **Option 1: Unity Package Manager** ⭐ **Recommended**

### **Step-by-Step:**

1. **Locate Package**
   ```
   Find the Synthesis_Package folder
   ```

2. **Copy to Packages Directory**
   ```
   ProjectRoot/
   ├── Assets/
   ├── Packages/              ← Copy here!
   │   └── Synthesis_Package/
   ├── ProjectSettings/
   └── ...
   ```

3. **Unity Auto-Import**
   - Unity will automatically detect and import the package
   - Check `Window → Package Manager` to verify
   - Look for "Synthesis" in the list

4. **Done!** ✅
   - Package is installed
   - All scripts available
   - Ready to use!

---

## **Option 2: Drop Into Assets** 

### **Step-by-Step:**

1. **Create Folder**
   ```
   Assets/
   └── Synthesis/  ← Create this folder
   ```

2. **Copy Files**
   ```
   Copy from Synthesis_Package/:
   - Runtime/ folder → Assets/Synthesis/Runtime/
   - Editor/ folder → Assets/Synthesis/Editor/
   ```

3. **Done!** ✅
   - Scripts imported as project assets
   - Fully integrated with your project

---

## **Option 3: Git Submodule** (For Version Control)

### **Step-by-Step:**

1. **Add as Submodule**
   ```bash
   cd YourUnityProject
   git submodule add https://github.com/your-repo/unity-bridge.git Packages/Synthesis
   ```

2. **Initialize**
   ```bash
   git submodule update --init --recursive
   ```

3. **Done!** ✅
   - Package tracked in version control
   - Easy to update with `git pull`

---

## **Verify Installation**

After installing, verify everything works:

### **1. Check Scripts**
- Open Unity
- Look for `Synthesis` namespace in your scripts
- Search for `Synthesis` component (Add Component window)

### **2. Check Menu Items**
- `Synthesis → Apply Recorded Changes` should appear in menu

### **3. Test Component**
- Create new GameObject
- Add Component → Search "Synthesis"
- Should find: `Synthesis`, `Synthesis Extended`, `Synthesis HTTP Server`

---

## **Quick Setup (After Installation)**

### **1. Create Bridge GameObject**

```
Hierarchy (Right-click) → Create Empty
Name: "Synthesis"
Add Component → "Synthesis"
```

### **2. Configure (Defaults are fine!)**

```
✅ Enable Bridge: checked
Poll Interval: 0.5
Commands File: synthesis_commands.json
Results File: synthesis_results.json
Logs File: synthesis_logs.txt
```

### **3. Optional: Add HTTP Server**

```
Add Component → "Synthesis HTTP Server"
✅ Enable Server: checked
Port: 8765
✅ Log Requests: checked
```

### **4. Optional: Add Extended Features**

```
Add Component → "Synthesis Extended"
✅ Enable Extended Commands: checked
Generated Assets Path: Assets/AI_Generated
(OpenAI API Key: set if using GenerateImage)
```

### **5. Press Play!**

```
Console should show:
🌉 Synthesis Initialized!
Commands: D:/YourProject/synthesis_commands.json
Results: D:/YourProject/synthesis_results.json
Logs: D:/YourProject/synthesis_logs.txt

Optional (if HTTP server enabled):
[SynthesisHTTPServer] 🚀 HTTP Server started on port 8765
[SynthesisHTTPServer] MCP can now control Unity in real-time!
```

---

## **Troubleshooting Installation**

### **"Scripts don't compile"**

**Issue:** Missing Newtonsoft.Json dependency

**Fix:**
```
1. Open Package Manager (Window → Package Manager)
2. Click '+' → Add package by name
3. Enter: com.unity.nuget.newtonsoft-json
4. Click 'Add'
```

Alternative:
```
Edit Packages/manifest.json and add:
{
  "dependencies": {
    "com.unity.nuget.newtonsoft-json": "3.0.2"
  }
}
```

### **"Component not found"**

**Issue:** Assembly definitions not loading

**Fix:**
```
1. Assets → Reimport All
2. Restart Unity Editor
3. Check Console for compilation errors
```

### **"Namespace not found"**

**Issue:** .asmdef files missing

**Fix:**
```
Ensure these files exist:
- Runtime/Synthesis.Runtime.asmdef
- Editor/Synthesis.Editor.asmdef

If using Option 2 (Assets folder), you might not need .asmdef files.
```

---

## **Uninstallation**

### **If installed via Package Manager:**
```
1. Delete Packages/Synthesis_Package folder
2. Unity will automatically unload
```

### **If installed via Assets folder:**
```
1. Delete Assets/Synthesis folder
2. Unity will remove all references
```

### **Clean up project files (optional):**
```
Delete these files from project root:
- synthesis_commands.json
- synthesis_results.json
- synthesis_logs.txt
```

---

## **Next Steps**

✅ **Installation Complete!**

Now what?

1. 📚 Read `README.md` for feature overview
2. 🚀 Read `Documentation/QUICK_START.md` to start using it
3. 📖 Read `Documentation/COMMANDS_REFERENCE.md` for all commands
4. 💡 Read `Documentation/EXAMPLES.md` for real-world use cases
5. 🔌 Read `Documentation/INTEGRATION_GUIDE.md` to connect your AI tool

---

## **Support**

- 📚 Check `Documentation/` folder for guides
- 🐛 Read `Documentation/TROUBLESHOOTING.md` for common issues
- 💬 Open an issue on GitHub

**Happy bridging!** 🌉✨

