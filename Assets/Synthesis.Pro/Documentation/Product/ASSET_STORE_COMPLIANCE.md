# Asset Store Compliance Analysis
**Synthesis.Pro - Asset Store Submission Readiness**

## CRITICAL BLOCKERS ⚠️

### 1. Embedded Executables (Section 1.5.a) - **BLOCKER**

**Requirement:**
> "The Asset Store is not accepting any submissions that include executables (for example, .exe, .apk, or other executables), embedded inside the package or as separate dependencies located in other websites."

**Current Status:** ❌ **VIOLATION**

**Issues Found:**
- `Assets/Synthesis.Pro/Server/node/node.exe` - Node.js runtime
- Multiple .exe files in Python distribution:
  - `pip/_vendor/distlib/*.exe` (6 executables)
  - `setuptools/*.exe` (8 executables)
  - `torch/bin/protoc.exe`
- Multiple .dll files in Python packages (numpy, scipy, torch, onnxruntime, etc.)

**Impact:** Asset Store will **REJECT** the submission

**Solutions:**
1. **Download on First Launch** (Recommended)
   - Remove embedded Python/Node from package
   - FirstTimeSetup.cs already has download logic
   - Download from GitHub releases or external CDN on first use
   - User clicks "First Time Setup" to download dependencies

2. **Separate Download Link**
   - Provide dependencies as separate download
   - Include setup script that fetches them
   - Document in installation guide

3. **Use System Python/Node**
   - Remove embedded runtimes entirely
   - Require users to install Python 3.10+ and Node.js
   - Detect system installations
   - More fragile, less user-friendly

**Recommended Action:** Use Solution #1 - already partially implemented in FirstTimeSetup.cs

---

### 2. Menu Placement (Section 2.5.1.a) - **VIOLATION**

**Requirement:**
> "File menus are placed under an existing menu, such as "Window/<PackageName>". If no existing menus are a good fit, they are placed under a custom menu called "Tools"."

**Current Status:** ❌ **VIOLATION**

**Issues Found:**
- Currently using top-level "Synthesis/" menu
- Should be "Window/Synthesis/" or "Tools/Synthesis/"

**Files to Fix:**
- `Assets/Synthesis.Pro/Editor/SynthesisEditorTools.cs:15` - Change MenuRoot to "Window/Synthesis/" or "Tools/Synthesis/"
- `Assets/Synthesis.Pro/Editor/SynthesisMenu.cs` - Update menu paths
- `Assets/Synthesis.Pro/Editor/FirstTimeSetup.cs` - Update menu paths
- `Assets/Synthesis.Pro/Editor/ExportPackage.cs` - Update menu path
- `Assets/Synthesis.Pro/Editor/PublicDBSync.cs` - Update menu paths

**Impact:** Asset Store will **REJECT** the submission

**Fix:** Simple find-replace to update menu paths

---

## REQUIRED FOR COMPLIANCE ⚠️

### 3. Third-Party Notices File (Section 1.2.a)

**Requirement:**
> "Your submission includes a Third-Party Notices text file listing fonts, audio, and other third-party components with dependent licenses."

**Current Status:** ❌ **MISSING**

**Required Dependencies to Document:**
- Newtonsoft.Json (MIT License)
- Python 3.10+ (PSF License)
- Node.js (MIT License)
- SQLite (Public Domain)
- Python packages: numpy, scipy, pandas, torch, onnxruntime, sklearn, sentence-transformers, etc.

**Impact:** Asset Store will **REJECT** the submission

**Action:** Create `Third-Party Notices.txt` in package root

---

### 4. No Errors or Warnings (Section 1.1.c)

**Requirement:**
> "Packages do not throw any errors or warnings that originate from package content after setup is complete."

**Current Status:** ✅ **FIXED** (Find-VisualStudio.cs renamed to .txt)

**Note:** Verify no other warnings exist before submission

---

### 5. API Key Storage (Section 1.5.b)

**Requirement:**
> "Third-party API keys are not stored in ways that would incorporate the key into project builds (for example, inside any script or GameObject that would be included in a scene)."

**Current Status:** ⚠️ **NEEDS VERIFICATION**

**Files to Check:**
- `Assets/Synthesis.Pro/Runtime/AnthropicAPIClient.cs` - Verify API key storage
- Ensure keys are stored in Editor-only scripts or EditorPrefs, not PlayerPrefs or scene data

---

### 6. Third-Party API Costs Disclosure (Section 1.5.c)

**Requirement:**
> "Packages that interact with third-party APIs must have Terms of API usage and additional costs, if applicable, clearly and transparently portrayed at the top of the listing's description and in the documentation."

**Current Status:** ⚠️ **NEEDS UPDATE**

**Action Required:**
Add to top of Asset Store description:
```
⚠️ THIRD-PARTY API USAGE

This package integrates with the Anthropic Claude API for AI functionality.
API usage requires:
- Anthropic API account (https://www.anthropic.com/)
- API key (obtained from Anthropic Console)
- API costs are billed directly by Anthropic based on usage

Approximate costs (as of 2026-02):
- Claude Sonnet: $3.00 per million input tokens, $15.00 per million output tokens
- Typical usage: ~$0.10-0.50 per AI session depending on project size

See Anthropic's pricing page for current rates: https://www.anthropic.com/pricing
```

---

## VERIFICATION NEEDED ⚠️

### 7. Code Namespaces (Section 2.5.a)

**Requirement:**
> "All code is contained in user declared namespaces. Code cannot be contained in official Unity namespaces or those that include Unity or any other trademarks."

**Current Status:** ⚠️ **NEEDS VERIFICATION**

**Action:** Verify all C# files use `Synthesis` or `Synthesis.*` namespaces, not `Unity.*` or `UnityEngine.*`

---

### 8. Documentation Completeness (Section 2.3.a)

**Requirement:**
> "Documentation is required if your package includes code or shaders, has configuration options, or requires setup. Local (offline) documentation must either be comprehensive and complete; or include setup instructions and link to online documentation."

**Current Status:** ✅ **LIKELY COMPLIANT**

**Documentation Present:**
- `Assets/Synthesis.Pro/Documentation/User/INSTALLATION.md`
- `README.md`
- `EFFICIENT_WORKFLOW.md`
- `Assets/Synthesis.Pro/Documentation/User/CHANGELOG.md`
- `Assets/Synthesis.Pro/Documentation/User/CONTRIBUTING.md`

**Action:** Verify completeness before submission

---

### 9. Package Size (Section 1.1.f)

**Requirement:**
> "Submissions are not more than 6GB in size."

**Current Status:** ⚠️ **NEEDS VERIFICATION**

**Action:** Check package size after removing embedded executables

---

### 10. File Path Length (Section 2.1.e)

**Requirement:**
> "File paths for assets are under 140 characters."

**Current Status:** ⚠️ **NEEDS VERIFICATION**

**Action:** Scan for long paths, especially in Python/Node dependencies

---

## RECOMMENDED IMPROVEMENTS

### 11. Demo Scene (Section 1.1.g)

**Requirement (for applicable categories):**
> "Tool submissions that manipulate external assets (for example audio files, texture files, mesh files) include sample assets for demonstration."

**Current Status:** ℹ️ **OPTIONAL FOR TOOLS CATEGORY**

**Recommendation:** Include a simple demo scene showing:
- SynLink setup
- Sample AI interaction
- Knowledge base usage

---

### 12. InitializeOnLoad Usage (Section 2.5.1.d)

**Requirement:**
> "Submissions do not contain any scripts that upon import and at any other point automatically and/or without user consent redirect users outside the Unity Editor... Methods using the InitializeOnLoad attribute must serve a functional purpose in the context of the package itself."

**Current Status:** ⚠️ **NEEDS VERIFICATION**

**Action:** Verify no InitializeOnLoad attributes automatically open URLs or redirect users

---

## COMPLIANCE SUMMARY

| Category | Status | Priority |
|----------|--------|----------|
| Embedded Executables | ❌ BLOCKER | CRITICAL |
| Menu Placement | ❌ VIOLATION | CRITICAL |
| Third-Party Notices | ❌ MISSING | HIGH |
| API Costs Disclosure | ⚠️ NEEDED | HIGH |
| No Warnings | ✅ FIXED | HIGH |
| API Key Storage | ⚠️ VERIFY | MEDIUM |
| Code Namespaces | ⚠️ VERIFY | MEDIUM |
| Documentation | ✅ LIKELY OK | MEDIUM |
| Package Size | ⚠️ VERIFY | LOW |
| File Path Length | ⚠️ VERIFY | LOW |

---

## NEXT STEPS

### Immediate (Before Submission)
1. ❌ **CRITICAL:** Remove embedded Python/Node executables, implement download-on-demand
2. ❌ **CRITICAL:** Fix menu placement (Synthesis → Window/Synthesis or Tools/Synthesis)
3. ❌ **REQUIRED:** Create Third-Party Notices.txt
4. ⚠️ **REQUIRED:** Add API cost disclosure to description
5. ⚠️ **VERIFY:** Check API key storage location
6. ⚠️ **VERIFY:** Verify all code uses Synthesis namespace

### Before Submission
7. ⚠️ **VERIFY:** Final check for warnings in Unity console
8. ⚠️ **VERIFY:** Check package size < 6GB
9. ⚠️ **VERIFY:** Scan for file paths > 140 characters
10. ⚠️ **VERIFY:** Check for InitializeOnLoad redirects

### Optional Improvements
11. 💡 Consider adding demo scene
12. 💡 Review documentation completeness

---

**Document Version:** 1.0
**Last Updated:** 2026-02-03
**Analysis Based On:** Unity Asset Store Technical Guidelines (2026)
