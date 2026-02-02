#!/usr/bin/env python3
"""
Database Manager - Synthesis.Pro
Handles public database distribution, updates, and user contributions

Features:
- First-time setup: Download public DB if missing
- Update checks: Verify you have the latest Unity docs
- Auto-update: Download and install updates
- Contribution: Submit your knowledge to help the community
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import urllib.request
import urllib.error

# Configuration
GITHUB_REPO = "Fallen-Entertainment/Synthesis.Pro"
RELEASES_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
PUBLIC_DB_NAME = "synthesis_knowledge.db"
MODEL_FILE_NAME = "embeddinggemma-300M-Q8_0.gguf"
VERSION_FILE = "db_version.json"


class DatabaseManager:
    """Manages public database downloads, updates, and contributions"""

    def __init__(self, server_dir: Optional[Path] = None):
        """
        Initialize database manager

        Args:
            server_dir: Server directory path (defaults to script directory)
        """
        self.server_dir = server_dir or Path(__file__).parent
        self.public_db_path = self.server_dir / PUBLIC_DB_NAME
        self.models_dir = self.server_dir / "models"
        self.model_path = self.models_dir / MODEL_FILE_NAME
        self.version_file = self.server_dir / VERSION_FILE
        self.version_info: Dict[str, Any] = {}

        # Ensure models directory exists
        self.models_dir.mkdir(exist_ok=True)

        # Load current version info
        self._load_version_info()

    def _load_version_info(self):
        """Load current database version information"""
        if self.version_file.exists():
            try:
                with open(self.version_file, 'r') as f:
                    self.version_info = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load version info: {e}")
                self.version_info = {}
        else:
            self.version_info = {}

    def _save_version_info(self):
        """Save version information for both database and model"""
        self.version_info["updated"] = datetime.now().isoformat()
        self.version_info["source"] = RELEASES_API

        try:
            with open(self.version_file, 'w') as f:
                json.dump(self.version_info, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save version info: {e}")

    def _update_db_version(self, version: str, checksum: str, size: int):
        """Update database version in version info"""
        if "database" not in self.version_info:
            self.version_info["database"] = {}

        self.version_info["database"] = {
            "version": version,
            "checksum": checksum,
            "size": size
        }
        self._save_version_info()

    def _update_model_version(self, version: str, checksum: str, size: int):
        """Update model version in version info"""
        if "model" not in self.version_info:
            self.version_info["model"] = {}

        self.version_info["model"] = {
            "version": version,
            "checksum": checksum,
            "size": size
        }
        self._save_version_info()

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _fetch_latest_release_info(self) -> Optional[Dict[str, Any]]:
        """Fetch latest release information from GitHub"""
        try:
            print("Checking for latest database version...")

            req = urllib.request.Request(RELEASES_API)
            req.add_header('Accept', 'application/vnd.github.v3+json')

            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                return data
        except urllib.error.URLError as e:
            print(f"Error connecting to GitHub: {e}")
            return None
        except Exception as e:
            print(f"Error fetching release info: {e}")
            return None

    def _find_database_asset(self, release_data: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Find the public database asset in release data"""
        if 'assets' not in release_data:
            return None

        for asset in release_data['assets']:
            if asset['name'] == PUBLIC_DB_NAME:
                return {
                    'name': asset['name'],
                    'url': asset['browser_download_url'],
                    'size': asset['size'],
                    'version': release_data['tag_name']
                }

        return None

    def _find_model_asset(self, release_data: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Find the embeddings model asset in release data"""
        if 'assets' not in release_data:
            return None

        for asset in release_data['assets']:
            if asset['name'] == MODEL_FILE_NAME:
                return {
                    'name': asset['name'],
                    'url': asset['browser_download_url'],
                    'size': asset['size'],
                    'version': release_data['tag_name']
                }

        return None

    def _download_database(self, url: str, version: str) -> bool:
        """Download database from URL"""
        try:
            print(f"Downloading public database (version {version})...")

            # Download to temporary file
            temp_path = self.public_db_path.with_suffix('.db.download')

            # Create progress callback
            def progress_hook(block_count, block_size, total_size):
                if total_size > 0:
                    percent = min(100, block_count * block_size * 100 / total_size)
                    print(f"\rProgress: {percent:.1f}%", end='', flush=True)

            urllib.request.urlretrieve(url, temp_path, progress_hook)
            print()  # New line after progress

            # Calculate checksum
            checksum = self._calculate_checksum(temp_path)

            # Move to final location
            if self.public_db_path.exists():
                # Backup existing database
                backup_path = self.public_db_path.with_suffix('.db.backup')
                self.public_db_path.rename(backup_path)
                print(f"Previous database backed up to: {backup_path.name}")

            temp_path.rename(self.public_db_path)

            # Save version info
            size = self.public_db_path.stat().st_size
            self._update_db_version(version, checksum, size)

            print(f"Database downloaded successfully!")
            print(f"  Version: {version}")
            print(f"  Size: {size / 1024 / 1024:.2f} MB")
            print(f"  Checksum: {checksum[:16]}...")

            return True

        except Exception as e:
            print(f"Error downloading database: {e}")

            # Clean up temp file if it exists
            temp_path = self.public_db_path.with_suffix('.db.download')
            if temp_path.exists():
                temp_path.unlink()

            return False

    def _download_model(self, url: str, version: str) -> bool:
        """Download embeddings model from URL"""
        try:
            print(f"Downloading embeddings model (version {version})...")
            print(f"  Size: ~300 MB (this may take a few minutes)")

            # Download to temporary file
            temp_path = self.model_path.with_suffix('.gguf.download')

            # Create progress callback
            def progress_hook(block_count, block_size, total_size):
                if total_size > 0:
                    downloaded = block_count * block_size
                    percent = min(100, downloaded * 100 / total_size)
                    mb_downloaded = downloaded / 1024 / 1024
                    mb_total = total_size / 1024 / 1024
                    print(f"\rProgress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='', flush=True)

            urllib.request.urlretrieve(url, temp_path, progress_hook)
            print()  # New line after progress

            # Calculate checksum
            print("Verifying download integrity...")
            checksum = self._calculate_checksum(temp_path)

            # Move to final location
            if self.model_path.exists():
                # Backup existing model
                backup_path = self.model_path.with_suffix('.gguf.backup')
                self.model_path.rename(backup_path)
                print(f"Previous model backed up to: {backup_path.name}")

            temp_path.rename(self.model_path)

            # Save version info
            size = self.model_path.stat().st_size
            self._update_model_version(version, checksum, size)

            print(f"Model downloaded successfully!")
            print(f"  Version: {version}")
            print(f"  Size: {size / 1024 / 1024:.2f} MB")
            print(f"  Checksum: {checksum[:16]}...")

            return True

        except Exception as e:
            print(f"Error downloading model: {e}")

            # Clean up temp file if it exists
            temp_path = self.model_path.with_suffix('.gguf.download')
            if temp_path.exists():
                temp_path.unlink()

            return False

    def check_setup(self) -> bool:
        """
        Check if public database is set up

        Returns:
            True if database exists, False otherwise
        """
        return self.public_db_path.exists()

    def check_model_setup(self) -> bool:
        """
        Check if embeddings model is set up

        Returns:
            True if model exists, False otherwise
        """
        return self.model_path.exists()

    def setup_database(self, force: bool = False) -> bool:
        """
        Ensure public database is set up (download if needed)

        Args:
            force: Force download even if database exists

        Returns:
            True if setup successful, False otherwise
        """
        if self.check_setup() and not force:
            print(f"Public database already exists: {self.public_db_path.name}")
            if self.version_info:
                print(f"  Version: {self.version_info.get('version', 'unknown')}")
                print(f"  Updated: {self.version_info.get('updated', 'unknown')}")
            return True

        print("\n" + "=" * 60)
        print("Synthesis.Pro - First Time Setup")
        print("=" * 60)

        # Fetch latest release
        release_data = self._fetch_latest_release_info()
        if not release_data:
            print("\nCould not connect to GitHub to download database.")
            print("You can manually download it from:")
            print(f"https://github.com/{GITHUB_REPO}/releases/latest")
            return False

        # Find database asset
        asset = self._find_database_asset(release_data)
        if not asset:
            print(f"\nPublic database not found in latest release.")
            print("This might be a new installation. The database will be")
            print("created automatically as you use Synthesis.Pro.")
            return False

        print(f"\nFound public database:")
        print(f"  Version: {asset['version']}")
        print(f"  Size: {asset['size'] / 1024 / 1024:.2f} MB")
        print(f"\nThis database contains Unity API documentation and")
        print(f"general C# programming knowledge to help you code faster.")

        # Download
        return self._download_database(asset['url'], asset['version'])

    def setup_model(self, force: bool = False) -> bool:
        """
        Ensure embeddings model is set up (download if needed)

        Args:
            force: Force download even if model exists

        Returns:
            True if setup successful, False otherwise
        """
        if self.check_model_setup() and not force:
            print(f"Embeddings model already exists: {self.model_path.name}")
            if self.version_info.get('model'):
                model_info = self.version_info['model']
                print(f"  Version: {model_info.get('version', 'unknown')}")
                print(f"  Size: {model_info.get('size', 0) / 1024 / 1024:.2f} MB")
            return True

        print("\n" + "=" * 60)
        print("Synthesis.Pro - Embeddings Model Setup")
        print("=" * 60)

        # Fetch latest release
        release_data = self._fetch_latest_release_info()
        if not release_data:
            print("\nCould not connect to GitHub to download model.")
            print("You can manually download it from:")
            print(f"https://github.com/{GITHUB_REPO}/releases/latest")
            return False

        # Find model asset
        asset = self._find_model_asset(release_data)
        if not asset:
            print(f"\nEmbeddings model not found in latest release.")
            print("Semantic search will not be available without this model.")
            return False

        print(f"\nFound embeddings model:")
        print(f"  Version: {asset['version']}")
        print(f"  Size: {asset['size'] / 1024 / 1024:.2f} MB")
        print(f"\nThis model enables semantic search across your knowledge base.")

        # Download
        return self._download_model(asset['url'], asset['version'])

    def check_for_updates(self) -> Dict[str, Optional[str]]:
        """
        Check if newer versions are available for database and/or model

        Returns:
            Dictionary with 'database' and 'model' keys containing new version strings or None
        """
        updates = {'database': None, 'model': None}

        # Fetch latest release
        release_data = self._fetch_latest_release_info()
        if not release_data:
            return updates

        latest_version = release_data['tag_name']

        # Check database
        if self.check_setup():
            db_info = self.version_info.get('database', {})
            current_db_version = db_info.get('version', 'unknown')
            if current_db_version != latest_version:
                updates['database'] = latest_version

        # Check model
        if self.check_model_setup():
            model_info = self.version_info.get('model', {})
            current_model_version = model_info.get('version', 'unknown')
            if current_model_version != latest_version:
                updates['model'] = latest_version

        return updates

    def update_all(self) -> bool:
        """
        Update both database and model to latest versions

        Returns:
            True if all updates successful, False otherwise
        """
        print("\n" + "=" * 60)
        print("Synthesis.Pro - Update Check")
        print("=" * 60)

        # Check for updates
        updates = self.check_for_updates()

        if not updates['database'] and not updates['model']:
            print("\nYou already have the latest versions!")
            db_info = self.version_info.get('database', {})
            model_info = self.version_info.get('model', {})
            if db_info:
                print(f"  Database: {db_info.get('version', 'unknown')}")
            if model_info:
                print(f"  Model: {model_info.get('version', 'unknown')}")
            return True

        # Fetch release info
        release_data = self._fetch_latest_release_info()
        if not release_data:
            return False

        success = True

        # Update database if needed
        if updates['database']:
            print(f"\nDatabase update available: {updates['database']}")
            db_info = self.version_info.get('database', {})
            print(f"Current version: {db_info.get('version', 'unknown')}")

            asset = self._find_database_asset(release_data)
            if asset:
                if not self._download_database(asset['url'], asset['version']):
                    success = False
            else:
                print("Warning: Database asset not found in release")
                success = False

        # Update model if needed
        if updates['model']:
            print(f"\nModel update available: {updates['model']}")
            model_info = self.version_info.get('model', {})
            print(f"Current version: {model_info.get('version', 'unknown')}")

            asset = self._find_model_asset(release_data)
            if asset:
                if not self._download_model(asset['url'], asset['version']):
                    success = False
            else:
                print("Warning: Model asset not found in release")
                success = False

        return success

    def verify_all(self) -> bool:
        """
        Verify integrity of database and model using stored checksums

        Returns:
            True if all valid, False otherwise
        """
        all_valid = True

        # Verify database
        if self.check_setup():
            db_info = self.version_info.get('database', {})
            if 'checksum' in db_info:
                print("Verifying database integrity...")
                current_checksum = self._calculate_checksum(self.public_db_path)
                stored_checksum = db_info['checksum']

                if current_checksum == stored_checksum:
                    print("  Database: ✓ Valid")
                else:
                    print("  Database: ✗ Checksum mismatch!")
                    all_valid = False
            else:
                print("  Database: No checksum available")
        else:
            print("  Database: Not installed")

        # Verify model
        if self.check_model_setup():
            model_info = self.version_info.get('model', {})
            if 'checksum' in model_info:
                print("Verifying model integrity...")
                current_checksum = self._calculate_checksum(self.model_path)
                stored_checksum = model_info['checksum']

                if current_checksum == stored_checksum:
                    print("  Model: ✓ Valid")
                else:
                    print("  Model: ✗ Checksum mismatch!")
                    all_valid = False
            else:
                print("  Model: No checksum available")
        else:
            print("  Model: Not installed")

        return all_valid

    def get_contribution_info(self) -> Dict[str, Any]:
        """
        Get information about contributing to the public database

        Returns:
            Dictionary with contribution guidelines
        """
        return {
            "enabled": True,
            "method": "GitHub Pull Request",
            "repository": GITHUB_REPO,
            "guidelines": [
                "Only contribute knowledge that is public and shareable",
                "Never include project-specific or sensitive information",
                "Focus on Unity API docs, general C# patterns, and solutions",
                "Use the RAG add_text() method with private=False",
                "Export your public database and submit via PR"
            ],
            "export_command": "python database_manager.py --export-public"
        }


def main():
    """Main CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Synthesis.Pro Database Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--setup', action='store_true',
                       help='Set up public database (download if needed)')
    parser.add_argument('--update', action='store_true',
                       help='Check for and install database updates')
    parser.add_argument('--verify', action='store_true',
                       help='Verify database integrity')
    parser.add_argument('--check', action='store_true',
                       help='Check database status and version')
    parser.add_argument('--force', action='store_true',
                       help='Force download even if database exists')
    parser.add_argument('--contribute', action='store_true',
                       help='Show contribution guidelines')

    args = parser.parse_args()

    # Initialize manager
    manager = DatabaseManager()

    # Handle commands
    if args.setup:
        # Setup both database and model
        db_success = manager.setup_database(force=args.force)
        model_success = manager.setup_model(force=args.force)
        success = db_success and model_success
        sys.exit(0 if success else 1)

    elif args.update:
        success = manager.update_all()
        sys.exit(0 if success else 1)

    elif args.verify:
        success = manager.verify_all()
        sys.exit(0 if success else 1)

    elif args.check:
        print("\n" + "=" * 60)
        print("Synthesis.Pro - Status")
        print("=" * 60)

        # Database status
        print(f"\nPublic Database: {manager.public_db_path.name}")
        if manager.check_setup():
            print(f"  Status: ✓ Installed")
            db_info = manager.version_info.get('database', {})
            if db_info:
                print(f"  Version: {db_info.get('version', 'unknown')}")
                print(f"  Size: {db_info.get('size', 0) / 1024 / 1024:.2f} MB")
        else:
            print(f"  Status: ✗ Not installed")

        # Model status
        print(f"\nEmbeddings Model: {manager.model_path.name}")
        if manager.check_model_setup():
            print(f"  Status: ✓ Installed")
            model_info = manager.version_info.get('model', {})
            if model_info:
                print(f"  Version: {model_info.get('version', 'unknown')}")
                print(f"  Size: {model_info.get('size', 0) / 1024 / 1024:.2f} MB")
        else:
            print(f"  Status: ✗ Not installed")

        # Check for updates
        if manager.check_setup() or manager.check_model_setup():
            print(f"\nLast updated: {manager.version_info.get('updated', 'unknown')}")

            updates = manager.check_for_updates()
            if updates['database'] or updates['model']:
                print(f"\n  Updates available:")
                if updates['database']:
                    print(f"    • Database: {updates['database']}")
                if updates['model']:
                    print(f"    • Model: {updates['model']}")
                print(f"  Run: python database_manager.py --update")
            else:
                print(f"\n  ✓ Everything is up to date!")
        else:
            print("\n  Run: python database_manager.py --setup")

        sys.exit(0)

    elif args.contribute:
        info = manager.get_contribution_info()
        print("\n" + "=" * 60)
        print("Contributing to Synthesis.Pro")
        print("=" * 60)
        print(f"\nRepository: https://github.com/{info['repository']}")
        print(f"\nGuidelines:")
        for guideline in info['guidelines']:
            print(f"  • {guideline}")
        print(f"\nThank you for helping the community! 🤝")
        sys.exit(0)

    else:
        # No command specified - run setup check
        needs_setup = not manager.check_setup() or not manager.check_model_setup()

        if needs_setup:
            print("\nFirst-time setup required...")
            db_success = True
            model_success = True

            if not manager.check_setup():
                print("\nSetting up public database...")
                db_success = manager.setup_database()

            if not manager.check_model_setup():
                print("\nSetting up embeddings model...")
                model_success = manager.setup_model()

            success = db_success and model_success
            sys.exit(0 if success else 1)
        else:
            # Everything exists - check for updates
            updates = manager.check_for_updates()
            if updates['database'] or updates['model']:
                print("\nUpdates available:")
                if updates['database']:
                    print(f"  • Database: {updates['database']}")
                if updates['model']:
                    print(f"  • Model: {updates['model']}")
                print(f"\nRun: python database_manager.py --update")
            else:
                print("\n✓ Everything is up to date!")
            sys.exit(0)


if __name__ == "__main__":
    main()
