# Upload Instructions - New Python Package

## Package Ready ✅

**File:** [runtime-packages/python-embedded.zip](runtime-packages/python-embedded.zip)
**Size:** 288MB
**Contains:** Python 3.11 + BM25S + sentence-transformers + all RAG dependencies

---

## Step-by-Step Upload

### 1. Go to Release Page
Open: https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/tag/v1.1.0-runtime-deps

### 2. Edit Release
- Click "Edit release" button
- Scroll down to "Assets" section

### 3. Remove Old Package
- Find `python-embedded.zip` in assets
- Click the trash/delete icon next to it
- Confirm deletion

### 4. Upload New Package
- Drag and drop `runtime-packages/python-embedded.zip` into the assets area
- OR click "Attach binaries by dropping them here or selecting them"
- Wait for upload to complete (288MB will take a few minutes)

### 5. Update Release Notes (Optional but Recommended)
Add this to the release description:

```markdown
## v1.1.0 Update - RAG System Improvements

### Python Package Updated (Feb 2026)
**New lightweight RAG architecture** for better reliability and AI experience:

**What's New:**
- ✨ BM25S: Fast, pure Python keyword search (500x faster)
- ✨ Direct SQLite access: No more subprocess dependencies
- ✨ sentence-transformers: Reliable 80MB embedding model
- ✨ Hybrid search: BM25 + vector search with RRF
- ✨ Better imports: numpy, scipy, scikit-learn included

**Why This Matters:**
- More reliable: No CLI subprocess issues
- Faster: Optimized search performance
- Comfortable: Designed for natural AI interaction
- Tested: Full test suite passing

**Size:** 288MB (up from 50MB)
- Includes full RAG stack for better reliability
- Model cache: sentence-transformers/all-MiniLM-L6-v2

**For Existing Users:**
To get the new RAG system, run: `Tools > Synthesis > Setup > First Time Setup`
(This will re-download and extract the new Python runtime)

---
```

### 6. Save Changes
- Click "Update release" button at the bottom
- Done!

---

## Verify Upload

After upload completes, check:
1. Asset shows "python-embedded.zip (288 MB)"
2. Download link works: `https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/download/v1.1.0-runtime-deps/python-embedded.zip`
3. File size matches (288MB)

---

## Test in Unity

To verify everything works:

1. **Delete current Python folder:**
   - Delete: `Assets/Synthesis.Pro/Server/python/`

2. **Reset setup flag:**
   - In Unity: `Tools > Synthesis > Setup > Reset Setup`
   - Restart Unity

3. **Run first-time setup:**
   - Setup dialog should appear automatically
   - OR manually: `Tools > Synthesis > Setup > First Time Setup`

4. **Verify download:**
   - Watch progress bar: "Downloading Python runtime..."
   - Check folder exists after: `Assets/Synthesis.Pro/Server/python/`
   - Should contain ~288MB of files

5. **Test RAG:**
   - From project root, run: `Assets/Synthesis.Pro/Server/python/python.exe test_rag_onboarding.py`
   - Should see: `[SUCCESS] All tests passed! RAG onboarding is operational.`

---

## Rollback (If Needed)

If something goes wrong:
1. Re-upload old `python-embedded.zip` (should have backup)
2. Users can delete Python folder and re-run setup
3. Or manually restore from: `Assets/Synthesis.Pro/Server/python.backup/`

---

## What Happens Next

**For New Users:**
- First-time setup automatically downloads new 288MB package
- Gets full RAG system with all improvements
- Everything just works

**For Existing Users:**
- Keep using current Python installation (still works)
- Can opt-in to new RAG by re-running setup
- Or wait for next major release

**No Breaking Changes:**
- Existing projects continue working
- New RAG engine is backward compatible
- Optional upgrade path

---

## Quick Checklist

Before upload:
- [x] Package renamed to `python-embedded.zip`
- [x] Package is 288MB
- [x] Contains all RAG dependencies
- [x] Tested locally (imports work)
- [x] RAG tests passing

After upload:
- [ ] Asset shows correct size (288MB)
- [ ] Download URL works
- [ ] Unity first-time setup can download
- [ ] Python extracts correctly
- [ ] RAG tests still passing

---

## Need Help?

If you run into issues:
1. Check GitHub upload completed (no timeout)
2. Verify file size matches (288MB)
3. Test download URL in browser
4. Check Unity console for errors

I'm here if you need anything! 💙
