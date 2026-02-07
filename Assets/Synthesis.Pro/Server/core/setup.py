"""
Synthesis.Pro Server Setup
Installs Python dependencies and configures the RAG engine
"""

import subprocess
import sys
import os
from pathlib import Path


def install_requirements():
    """Install Python requirements"""
    print("📦 Installing Python dependencies...")

    rag_dir = Path(__file__).parent.parent / "RAG"
    requirements_file = rag_dir / "requirements.txt"

    if not requirements_file.exists():
        print(f"❌ Requirements file not found: {requirements_file}")
        return False

    try:
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            str(requirements_file)
        ])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def download_embedding_model():
    """Download default embedding model for local RAG"""
    print("\n📥 Downloading embedding model...")
    print("This may take a few minutes on first run...")

    try:
        result = subprocess.run([
            "sqlite-rag",
            "download-model",
            "unsloth/embeddinggemma-300m-GGUF",
            "embeddinggemma-300M-Q8_0.gguf"
        ], capture_output=True, text=True)

        if result.returncode == 0 or "already exists" in result.stdout:
            print("✅ Embedding model ready!")
            return True
        else:
            print(f"⚠️  Model download issue: {result.stderr}")
            print("You can skip this for now and use OpenAI embeddings instead.")
            return True  # Don't fail setup for this
    except FileNotFoundError:
        print("⚠️  sqlite-rag CLI not found. Dependencies may not be installed yet.")
        return False


def setup_knowledge_base():
    """Initialize the knowledge base"""
    print("\n🧠 Setting up knowledge base...")

    kb_dir = Path(__file__).parent.parent / "KnowledgeBase"
    kb_dir.mkdir(exist_ok=True)

    db_path = kb_dir / "synthesis_knowledge.db"

    print(f"Knowledge base will be created at: {db_path}")
    print("✅ Knowledge base directory ready!")
    return True


def main():
    """Main setup routine"""
    print("=" * 60)
    print("Synthesis.Pro Server Setup")
    print("=" * 60)
    print()

    success = True

    # Step 1: Install requirements
    if not install_requirements():
        success = False

    # Step 2: Download model (optional)
    if success:
        download_embedding_model()

    # Step 3: Setup knowledge base
    if success:
        setup_knowledge_base()

    print()
    print("=" * 60)
    if success:
        print("✅ Setup complete!")
        print()
        print("Next steps:")
        print("1. Open Unity and add SynLink component to a GameObject")
        print("2. Use the RAG engine: from rag_engine_lite import SynthesisRAG")
        print("3. Check Documentation folder for guides")
    else:
        print("❌ Setup failed. Please check errors above.")
    print("=" * 60)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
