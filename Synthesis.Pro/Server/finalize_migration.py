#!/usr/bin/env python3
"""
Finalize Migration Script
Copies embedded Python and prepares for prototype deletion
"""

import shutil
import sys
from pathlib import Path


def main():
    print("=" * 60)
    print("Synthesis.Pro Migration Finalization")
    print("=" * 60)

    # Paths
    root = Path(__file__).parent.parent.parent
    prototype_python = root / "Assets" / "Synthesis_AI" / "KnowledgeBase" / "python"
    target_python = Path(__file__).parent / "python"

    # Check if prototype Python exists
    if not prototype_python.exists():
        print("ERROR: Prototype Python not found!")
        print(f"   Looking for: {prototype_python}")
        return 1

    # Copy Python runtime
    print(f"\nCopying Python runtime...")
    print(f"   From: {prototype_python}")
    print(f"   To: {target_python}")

    if target_python.exists():
        print("   Target already exists, removing...")
        shutil.rmtree(target_python)

    shutil.copytree(prototype_python, target_python)
    print("   [OK] Python runtime copied")

    # Verify Python works
    python_exe = target_python / "python.exe"
    if not python_exe.exists():
        python_exe = target_python / "python"  # Unix

    if python_exe.exists():
        import subprocess
        result = subprocess.run(
            [str(python_exe), "--version"],
            capture_output=True,
            text=True
        )
        print(f"   [OK] Python verified: {result.stdout.strip()}")

    # Check databases
    server_dir = Path(__file__).parent
    public_db = server_dir / "synthesis_knowledge.db"
    private_db = server_dir / "synthesis_private.db"

    print(f"\nDatabase Status:")
    if public_db.exists():
        size = public_db.stat().st_size / (1024 * 1024)
        print(f"   [OK] Public: {public_db.name} ({size:.2f} MB)")
    else:
        print(f"   [ERROR] Public database not found!")
        return 1

    if private_db.exists():
        size = private_db.stat().st_size / (1024 * 1024)
        print(f"   [OK] Private: {private_db.name} ({size:.2f} MB)")
    else:
        print(f"   [ERROR] Private database not found!")
        return 1

    print("\n" + "=" * 60)
    print("FINALIZATION COMPLETE")
    print("=" * 60)
    print("\nSafe to delete:")
    print(f"   Assets/Synthesis_AI/")
    print("\nRemaining manual steps:")
    print("   1. Remove SynLinkEditor.cs from Synthesis.Pro/Editor/")
    print("   2. Remove SynthesisEditorTools.cs from Synthesis.Pro/Editor/")
    print("   3. Update SynthesisMenu.cs to remove old HTTP server menu items")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
