# Deployment Plan - New RAG Python Package

## Current Status

✅ **Built:** New Python package with RAG dependencies (288MB)
- Location: [runtime-packages/python-embedded-rag.zip](runtime-packages/python-embedded-rag.zip)
- Contains: BM25S, sentence-transformers, numpy, scipy, scikit-learn
- Tested: All imports working, RAG functional

❌ **Not Yet Deployed:** Package needs to be uploaded to GitHub releases

## How Unity Gets the Package

Unity's [FirstTimeSetup.cs](Assets/Synthesis.Pro/Editor/FirstTimeSetup.cs) downloads from:

```csharp
private const string PYTHON_DOWNLOAD_URL =
    "https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/download/v1.1.0-runtime-deps/python-embedded.zip";
```

**Current release tag:** `v1.1.0-runtime-deps`
**Expected filename:** `python-embedded.zip` (not `python-embedded-rag.zip`)

## Deployment Options

### Option 1: Update Existing Release (Recommended)
**Pros:**
- No code changes needed
- Existing FirstTimeSetup.cs continues to work
- Clean update path

**Cons:**
- Users who already downloaded old package will keep using it
- Breaking change for existing installations (might need re-setup)

**Steps:**
1. Rename `python-embedded-rag.zip` to `python-embedded.zip`
2. Go to: https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/tag/v1.1.0-runtime-deps
3. Delete old `python-embedded.zip` asset
4. Upload new `python-embedded.zip` (288MB)
5. Update release notes to mention RAG improvements

**Impact:** New users get new package automatically

---

### Option 2: Create New Release Tag
**Pros:**
- Old installations not affected
- Clear versioning and changelog
- Can test before switching

**Cons:**
- Need to update FirstTimeSetup.cs
- Need to create new release

**Steps:**
1. Rename `python-embedded-rag.zip` to `python-embedded.zip`
2. Create new release: `v1.2.0-runtime-deps`
3. Upload all three packages:
   - `python-embedded.zip` (new, 288MB)
   - `node-embedded.zip` (copy from v1.1.0)
   - `models.zip` (copy from v1.1.0)
4. Update FirstTimeSetup.cs URLs:
   ```csharp
   private const string PYTHON_DOWNLOAD_URL =
       "https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/download/v1.2.0-runtime-deps/python-embedded.zip";
   // Update NODE and MODELS URLs similarly
   ```

**Impact:** Need code update, but clean versioning

---

### Option 3: Patch Release
**Pros:**
- Semantic versioning (1.1.1 = patch)
- Shows it's a minor update
- Clean history

**Cons:**
- Still need to update FirstTimeSetup.cs
- Need to copy other packages

**Steps:**
1. Same as Option 2, but use `v1.1.1-runtime-deps`
2. Update FirstTimeSetup.cs URLs to `v1.1.1-runtime-deps`

---

## Recommended Approach

**I recommend Option 1** because:
- Fastest path to deployment
- No code changes
- New users automatically get the improved package
- Existing users can re-run setup if they want the new features

### Quick Action Steps (Option 1)

1. **Rename the package:**
   ```bash
   cd runtime-packages
   mv python-embedded-rag.zip python-embedded.zip
   ```

2. **Upload to GitHub:**
   - Go to: https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/tag/v1.1.0-runtime-deps
   - Edit release
   - Delete old `python-embedded.zip`
   - Upload new `python-embedded.zip`
   - Update release notes

3. **Test:**
   - Delete `Assets/Synthesis.Pro/Server/python/` folder
   - Run Unity first-time setup
   - Verify new package downloads and RAG works

4. **Optional - Notify existing users:**
   - Create announcement about RAG improvements
   - Mention they can re-run setup: `Tools > Synthesis > Setup > First Time Setup`
   - Or manually replace python folder

---

## Files to Update (If choosing Option 2 or 3)

### [Assets/Synthesis.Pro/Editor/FirstTimeSetup.cs](Assets/Synthesis.Pro/Editor/FirstTimeSetup.cs)

Lines 17-19:
```csharp
private const string PYTHON_DOWNLOAD_URL = "https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/download/v1.2.0-runtime-deps/python-embedded.zip";
private const string NODE_DOWNLOAD_URL = "https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/download/v1.2.0-runtime-deps/node-embedded.zip";
private const string MODELS_DOWNLOAD_URL = "https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/download/v1.2.0-runtime-deps/models.zip";
```

---

## Package Details

**Old Package (v1.1.0):**
- Size: ~50MB
- Dependencies: Basic Python with minimal packages
- RAG: Uses sqlite-rag CLI (unreliable)

**New Package (v1.2.0):**
- Size: 288MB
- Dependencies: Full RAG stack (numpy, scipy, bm25s, sentence-transformers)
- RAG: Direct Python implementation (reliable, fast, comfortable)
- Model: sentence-transformers/all-MiniLM-L6-v2 (~80MB)

**Size increase:** +238MB (from 50MB to 288MB)
- Justified by: Improved reliability, better AI experience, no subprocess dependencies

---

## Testing Checklist

After deployment:
- [ ] First-time setup downloads successfully
- [ ] Python extracts to correct location
- [ ] All RAG dependencies import correctly
- [ ] Model downloads and caches properly
- [ ] Search functions work (BM25, vector, hybrid)
- [ ] Onboarding system integrates smoothly
- [ ] No errors in Unity console

---

## Rollback Plan

If issues occur:
1. Re-upload old `python-embedded.zip` from v1.1.0 backup
2. Users can clear `Synthesis.SetupComplete` EditorPref and re-run setup
3. Or manually restore old python folder from backup

---

## What I Need from You

To proceed, I need to know:
1. Which option do you prefer? (1, 2, or 3)
2. Do you want me to rename the package?
3. Manual upload to GitHub, or should I prepare instructions?

**My recommendation:** Option 1 - just replace the package in the existing release. Fastest and simplest.

Let me know what you'd like to do and I'll execute it! ☕
