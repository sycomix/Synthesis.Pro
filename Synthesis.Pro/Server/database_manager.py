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
        self.version_file = self.server_dir / VERSION_FILE
        self.version_info: Dict[str, Any] = {}

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

    def _save_version_info(self, version: str, checksum: str, size: int):
        """Save database version information"""
        self.version_info = {
            "version": version,
            "checksum": checksum,
            "size": size,
            "updated": datetime.now().isoformat(),
            "source": RELEASES_API
        }

        try:
            with open(self.version_file, 'w') as f:
                json.dump(self.version_info, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save version info: {e}")

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
            self._save_version_info(version, checksum, size)

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

    def check_setup(self) -> bool:
        """
        Check if public database is set up

        Returns:
            True if database exists, False otherwise
        """
        return self.public_db_path.exists()

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

    def check_for_updates(self) -> Optional[str]:
        """
        Check if a newer database version is available

        Returns:
            New version string if available, None otherwise
        """
        if not self.check_setup():
            return None  # No current database to update

        # Fetch latest release
        release_data = self._fetch_latest_release_info()
        if not release_data:
            return None

        # Find database asset
        asset = self._find_database_asset(release_data)
        if not asset:
            return None

        # Compare versions
        current_version = self.version_info.get('version', 'unknown')
        latest_version = asset['version']

        if current_version != latest_version:
            return latest_version

        return None

    def update_database(self) -> bool:
        """
        Update public database to latest version

        Returns:
            True if updated successfully, False otherwise
        """
        print("\n" + "=" * 60)
        print("Synthesis.Pro - Database Update")
        print("=" * 60)

        # Check for updates
        new_version = self.check_for_updates()
        if not new_version:
            print("\nYou already have the latest database version!")
            if self.version_info:
                print(f"  Current version: {self.version_info.get('version', 'unknown')}")
            return True

        print(f"\nNew version available: {new_version}")
        print(f"Current version: {self.version_info.get('version', 'unknown')}")

        # Fetch release info
        release_data = self._fetch_latest_release_info()
        if not release_data:
            return False

        # Find database asset
        asset = self._find_database_asset(release_data)
        if not asset:
            return False

        # Download update
        return self._download_database(asset['url'], asset['version'])

    def verify_database(self) -> bool:
        """
        Verify database integrity using stored checksum

        Returns:
            True if valid, False otherwise
        """
        if not self.check_setup():
            print("Public database not found")
            return False

        if 'checksum' not in self.version_info:
            print("No checksum available for verification")
            return False

        print("Verifying database integrity...")
        current_checksum = self._calculate_checksum(self.public_db_path)
        stored_checksum = self.version_info['checksum']

        if current_checksum == stored_checksum:
            print("Database verified successfully!")
            return True
        else:
            print("Warning: Database checksum mismatch!")
            print("The database may be corrupted. Consider re-downloading.")
            return False

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
        success = manager.setup_database(force=args.force)
        sys.exit(0 if success else 1)

    elif args.update:
        success = manager.update_database()
        sys.exit(0 if success else 1)

    elif args.verify:
        success = manager.verify_database()
        sys.exit(0 if success else 1)

    elif args.check:
        print("\n" + "=" * 60)
        print("Database Status")
        print("=" * 60)

        if manager.check_setup():
            print(f"\nPublic database: {manager.public_db_path.name}")
            print(f"  Status: Installed")

            if manager.version_info:
                print(f"  Version: {manager.version_info.get('version', 'unknown')}")
                print(f"  Size: {manager.version_info.get('size', 0) / 1024 / 1024:.2f} MB")
                print(f"  Updated: {manager.version_info.get('updated', 'unknown')}")

            # Check for updates
            new_version = manager.check_for_updates()
            if new_version:
                print(f"\n  Update available: {new_version}")
                print(f"  Run: python database_manager.py --update")
            else:
                print(f"\n  You have the latest version!")
        else:
            print("\nPublic database: Not installed")
            print("  Run: python database_manager.py --setup")

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
        if not manager.check_setup():
            print("\nPublic database not found. Running first-time setup...")
            success = manager.setup_database()
            sys.exit(0 if success else 1)
        else:
            # Database exists - check for updates
            new_version = manager.check_for_updates()
            if new_version:
                print(f"\nUpdate available: {new_version}")
                print(f"Run: python database_manager.py --update")
            else:
                print("\nDatabase is up to date!")
            sys.exit(0)


if __name__ == "__main__":
    main()
