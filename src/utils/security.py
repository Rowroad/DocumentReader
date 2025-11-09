"""Security and privacy utilities."""

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Tuple
from cryptography.fernet import Fernet
import json


class SecurityManager:
    """Manages security and privacy features."""

    def __init__(self, temp_directory: str, encryption_key: bytes = None):
        """Initialize security manager.

        Args:
            temp_directory: Temporary storage directory
            encryption_key: Encryption key for local storage (generated if None)
        """
        self.temp_directory = Path(temp_directory)
        self.temp_directory.mkdir(parents=True, exist_ok=True)

        # Encryption
        if encryption_key:
            self.cipher = Fernet(encryption_key)
        else:
            # Generate new key
            self.cipher = Fernet(Fernet.generate_key())

        # Metadata file to track stored files
        self.metadata_file = self.temp_directory / "storage_metadata.json"
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> dict:
        """Load storage metadata."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_metadata(self):
        """Save storage metadata."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2, default=str)

    def store_file_encrypted(self, file_path: Path, data: bytes) -> Path:
        """Store a file with encryption.

        Args:
            file_path: Relative path for the file
            data: File data to encrypt and store

        Returns:
            Path to stored encrypted file
        """
        # Encrypt data
        encrypted_data = self.cipher.encrypt(data)

        # Store file
        full_path = self.temp_directory / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, 'wb') as f:
            f.write(encrypted_data)

        # Update metadata
        self.metadata[str(file_path)] = {
            'stored_at': datetime.now().isoformat(),
            'size': len(data)
        }
        self._save_metadata()

        return full_path

    def read_file_encrypted(self, file_path: Path) -> bytes:
        """Read and decrypt a file.

        Args:
            file_path: Relative path to the file

        Returns:
            Decrypted file data
        """
        full_path = self.temp_directory / file_path

        with open(full_path, 'rb') as f:
            encrypted_data = f.read()

        # Decrypt
        return self.cipher.decrypt(encrypted_data)

    def cleanup_old_files(self, days: int = 7, auto: bool = False) -> Tuple[int, List[str]]:
        """Clean up files older than specified days.

        Args:
            days: Number of days to keep files
            auto: If True, delete without confirmation

        Returns:
            Tuple of (number of files deleted, list of deleted file paths)
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_files = []
        deleted_count = 0

        # Check metadata for old files
        for file_path, metadata in list(self.metadata.items()):
            stored_at = datetime.fromisoformat(metadata['stored_at'])

            if stored_at < cutoff_date:
                full_path = self.temp_directory / file_path

                if full_path.exists():
                    if auto:
                        full_path.unlink()
                        deleted_files.append(str(file_path))
                        deleted_count += 1

                # Remove from metadata
                if auto:
                    del self.metadata[file_path]

        if auto:
            self._save_metadata()

        return deleted_count, deleted_files

    def get_storage_info(self) -> dict:
        """Get information about stored files.

        Returns:
            Dictionary with storage statistics
        """
        total_size = 0
        file_count = len(self.metadata)
        oldest_file = None
        oldest_date = None

        for file_path, metadata in self.metadata.items():
            total_size += metadata.get('size', 0)

            stored_at = datetime.fromisoformat(metadata['stored_at'])
            if oldest_date is None or stored_at < oldest_date:
                oldest_date = stored_at
                oldest_file = file_path

        return {
            'file_count': file_count,
            'total_size_mb': total_size / (1024 * 1024),
            'oldest_file': oldest_file,
            'oldest_date': oldest_date.isoformat() if oldest_date else None
        }

    def purge_all_files(self):
        """Delete all stored files."""
        # Delete all files in temp directory except metadata
        for item in self.temp_directory.iterdir():
            if item.is_file() and item != self.metadata_file:
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

        # Clear metadata
        self.metadata = {}
        self._save_metadata()

    def secure_delete_file(self, file_path: Path):
        """Securely delete a file by overwriting before deletion.

        Args:
            file_path: Path to file to delete
        """
        if not file_path.exists():
            return

        # Get file size
        file_size = file_path.stat().st_size

        # Overwrite with random data
        with open(file_path, 'wb') as f:
            f.write(os.urandom(file_size))

        # Delete file
        file_path.unlink()

        # Remove from metadata
        relative_path = str(file_path.relative_to(self.temp_directory))
        if relative_path in self.metadata:
            del self.metadata[relative_path]
            self._save_metadata()

    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key format.

        Args:
            api_key: API key to validate

        Returns:
            True if format is valid
        """
        # Basic validation - actual keys should be validated with API
        if not api_key:
            return False

        # Google API keys typically start with "AIza" and are 39 characters
        return len(api_key) >= 30

    def get_files_for_cleanup(self, days: int = 7) -> List[Tuple[str, datetime, int]]:
        """Get list of files that would be deleted in cleanup.

        Args:
            days: Number of days threshold

        Returns:
            List of tuples (file_path, stored_date, size_bytes)
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        files_to_delete = []

        for file_path, metadata in self.metadata.items():
            stored_at = datetime.fromisoformat(metadata['stored_at'])

            if stored_at < cutoff_date:
                files_to_delete.append((
                    file_path,
                    stored_at,
                    metadata.get('size', 0)
                ))

        return files_to_delete
