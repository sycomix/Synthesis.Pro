#!/usr/bin/env python3
"""Quick test to verify RAG onboarding system is wired up"""
import sys
from pathlib import Path

# Add paths (script is in scripts/development/, need to go up to root)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "Assets" / "Synthesis.Pro" / "Server"))
sys.path.insert(0, str(project_root / "Assets" / "Synthesis.Pro" / "Server" / "rag_integration"))
sys.path.insert(0, str(project_root / "Assets" / "Synthesis.Pro" / "RAG" / "core"))

try:
    print("Testing RAG imports...")
    from rag_engine_lite import SynthesisRAG
    print("[OK] SynthesisRAG (lightweight) imported")

    from rag_onboarding import RAGOnboardingSystem
    print("[OK] RAGOnboardingSystem imported")

    # Test initialization
    print("\nTesting initialization...")
    db_path = project_root / "Assets" / "Synthesis.Pro" / "Server" / "database"
    rag = SynthesisRAG(
        database=str(db_path / "synthesis_knowledge.db"),
        private_database=str(db_path / "synthesis_private.db")
    )
    print("[OK] RAG engine initialized")

    onboarding = RAGOnboardingSystem(
        rag_engine=rag,
        user_id="test",
        presentation_style="natural"
    )
    print("[OK] Onboarding system initialized")

    # Test processing
    print("\nTesting message processing...")
    result = onboarding.process_user_message("What did we work on with VFX?")
    if result:
        print(f"[OK] Context detected: {result.get('has_context', False)}")
        if result.get('context'):
            print(f"  Preview: {result['context'][:100]}...")
    else:
        print("  No context offered (normal for new topics)")

    print("\n[SUCCESS] All tests passed! RAG onboarding is operational.")

except ImportError as e:
    print(f"\n[ERROR] Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
