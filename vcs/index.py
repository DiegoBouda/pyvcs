import json
from pathlib import Path
from typing import Dict

from .repo import Repository
from .storage import ObjectStore
from .objects import Blob


class IndexError(Exception):
    pass


class Index:
    def __init__(self, repo: Repository):
        self.repo = repo
        self.index_path = repo.index_file
        self.entries: Dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        """
        Load index from disk.
        """
        if not self.index_path.exists():
            self.entries = {}
            return

        content = self.index_path.read_text().strip()
        if not content:
            self.entries = {}
            return

        self.entries = json.loads(content)

    def _save(self) -> None:
        """
        Persist index to disk.
        """
        self.index_path.write_text(
            json.dumps(self.entries, sort_keys=True, indent=2)
        )

    def add(self, path: Path, store: ObjectStore) -> None:
        """
        Add a file to the staging area.
        """
        path = path.resolve()

        if not path.exists():
            raise IndexError(f"File not found: {path}")

        if not path.is_file():
            raise IndexError("Only files can be added")

        if not path.is_relative_to(self.repo.root):
            raise IndexError("File must be inside the repository")

        rel_path = path.relative_to(self.repo.root).as_posix()

        data = path.read_bytes()
        blob = Blob(data)
        blob_hash = blob.store(store)

        self.entries[rel_path] = blob_hash
        self._save()

    def remove(self, path: Path) -> None:
        """
        Remove a file from the staging area.
        """
        rel_path = path.as_posix()
        if rel_path not in self.entries:
            raise IndexError("File not staged")

        del self.entries[rel_path]
        self._save()

    def clear(self) -> None:
        """
        Clear the staging area.
        """
        self.entries = {}
        self._save()

    def list_entries(self) -> Dict[str, str]:
        """
        Return staged files.
        """
        return dict(self.entries)