import hashlib
from pathlib import Path
from typing import Tuple

from .repo import Repository


class StorageError(Exception):
    pass


class ObjectStore:
    def __init__(self, repo: Repository):
        self.repo = repo
        self.objects_dir = repo.objects_dir

    def _hash_object(self, data: bytes) -> str:
        """
        Compute SHA-1 hash of the object data.
        """
        h = hashlib.sha1()
        h.update(data)
        return h.hexdigest()

    def _object_path(self, obj_hash: str) -> Path:
        """
        Return the filesystem path for a given object hash.
        """
        return self.objects_dir / obj_hash[:2] / obj_hash[2:]

    def store(self, data: bytes) -> str:
        """
        Store raw object data and return its hash.
        Objects are immutable and content-addressed.
        """
        obj_hash = self._hash_object(data)
        obj_path = self._object_path(obj_hash)

        if obj_path.exists():
            return obj_hash  # already stored

        obj_path.parent.mkdir(parents=True, exist_ok=True)
        obj_path.write_bytes(data)

        return obj_hash

    def load(self, obj_hash: str) -> bytes:
        """
        Load raw object data by hash.
        """
        obj_path = self._object_path(obj_hash)

        if not obj_path.exists():
            raise StorageError(f"Object {obj_hash} not found")

        return obj_path.read_bytes()

    def exists(self, obj_hash: str) -> bool:
        """
        Check if an object exists.
        """
        return self._object_path(obj_hash).exists()