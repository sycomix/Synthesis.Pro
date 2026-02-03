"""
Quick RAG session for VFX Asset Creation investigation
Demonstrates the RAG-first workflow
"""
import sys
sys.path.insert(0, 'RAG')

from rag_engine import SynthesisRAG
from conversation_tracker import ConversationTracker
from datetime import datetime

print("=" * 70)
print("RAG-First Workflow: VFX Asset Creation Investigation")
print("=" * 70)

# Initialize RAG
print("\n[1/4] Initializing RAG engine...")
try:
    rag = SynthesisRAG(
        database="synthesis_knowledge.db",
        private_database="synthesis_private.db",
        embedding_provider="local"
    )
    print("[OK] RAG engine initialized (dual database mode)")
except Exception as e:
    print(f"[WARN] RAG init warning: {e}")
    print("  Continuing with available functionality...")

# Initialize conversation tracker
print("\n[2/4] Setting up conversation tracker...")
try:
    tracker = ConversationTracker(rag)
    print("[OK] Conversation tracker ready")
except Exception as e:
    print(f"[WARN] Tracker warning: {e}")

# Log quick note about the finding
print("\n[3/4] Logging findings to private KB...")
try:
    rag.quick_note(
        "VFX asset creation issue at ManageVFX.cs:216 - Currently using reflection "
        "to access internal Unity APIs (VisualEffectAssetEditorUtility.CreateNewAsset "
        "and VisualEffectResource.CreateNewAsset). Need authenticated/public API approach."
    )
    print("[OK] Logged quick note about VFX reflection issue")

    rag.log_decision(
        what="Using reflection for VFX asset creation",
        why="No public Unity API appears to be available for programmatic VFX Graph asset creation",
        alternatives="Options: 1) Find official Unity VFX Graph API, 2) Use MenuItem/EditorUtility approach, 3) Template-based creation"
    )
    print("[OK] Logged decision rationale")

    # Log the investigation context
    tracker.add_learning(
        observation="VFX Graph asset creation requires internal Unity API access - no public API documented",
        category="unity-limitation"
    )
    print("[OK] Logged learning observation")

except Exception as e:
    print(f"[WARN] Logging warning: {e}")

# Search KB for VFX solutions
print("\n[4/4] Searching KB for VFX/Unity solutions...")
search_queries = [
    "Unity VFX Graph create asset programmatically",
    "Unity Visual Effect Graph API MenuItem",
    "Unity ScriptableObject asset creation pattern",
    "Unity Editor internal API reflection best practices"
]

for query in search_queries:
    try:
        print(f"\n  Searching: '{query}'")
        results = rag.search(
            query=query,
            top_k=3,
            search_type="hybrid",
            scope="both"
        )

        if results:
            print(f"  [OK] Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                score = result.get('score', 0)
                text = result.get('text', '')[:150]
                source = result.get('source', 'unknown')
                print(f"    {i}. [{source}] (score: {score:.3f})")
                print(f"       {text}...")
        else:
            print(f"  [NONE] No results found")

    except Exception as e:
        print(f"  [ERROR] Search error: {e}")

# Checkpoint this investigation
print("\n" + "=" * 70)
print("Checkpointing investigation...")
try:
    rag.checkpoint(
        phase="VFX_Asset_Creation_Research",
        status="Logged findings, searched KB for solutions",
        next_steps="1) Check Unity forums/docs for official API, 2) Test MenuItem approach, 3) Consider template-based workflow"
    )
    print("[OK] Checkpoint saved to private DB")
except Exception as e:
    print(f"[WARN] Checkpoint warning: {e}")

print("\n" + "=" * 70)
print("Session Summary:")
print("- Logged VFX reflection issue to KB")
print("- Recorded decision rationale")
print("- Searched for Unity VFX solutions")
print("- Created checkpoint for next session")
print("\nContext saved! Next session will have this knowledge immediately available.")
print("=" * 70)
