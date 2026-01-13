from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Dict, Optional

from .storage import ObjectStore


class ObjectError(Exception):
    pass


# ---------- Base helpers ----------

def _encode(obj: dict) -> bytes:
    """
    Deterministic JSON encoding.
    Sorted keys ensure stable hashes.
    """
    return json.dumps(obj, sort_keys=True).encode("utf-8")


def _decode(data: bytes) -> dict:
    return json.loads(data.decode("utf-8"))


# ---------- Blob ----------

@dataclass(frozen=True)
class Blob:
    data: bytes

    def serialize(self) -> bytes:
        return self.data

    @staticmethod
    def deserialize(data: bytes) -> "Blob":
        return Blob(data=data)

    def store(self, store: ObjectStore) -> str:
        return store.store(self.serialize())


# ---------- Tree ----------

@dataclass(frozen=True)
class Tree:
    """
    Maps name -> object hash (blob or subtree)
    """
    entries: Dict[str, str]

    def serialize(self) -> bytes:
        payload = {
            "type": "tree",
            "entries": self.entries,
        }
        return _encode(payload)

    @staticmethod
    def deserialize(data: bytes) -> "Tree":
        payload = _decode(data)
        if payload.get("type") != "tree":
            raise ObjectError("Invalid tree object")
        return Tree(entries=payload["entries"])

    def store(self, store: ObjectStore) -> str:
        return store.store(self.serialize())


# ---------- Commit ----------

@dataclass(frozen=True)
class Commit:
    tree: str
    parent: Optional[str]
    message: str
    timestamp: int

    def serialize(self) -> bytes:
        payload = {
            "type": "commit",
            "tree": self.tree,
            "parent": self.parent,
            "message": self.message,
            "timestamp": self.timestamp,
        }
        return _encode(payload)

    @staticmethod
    def deserialize(data: bytes) -> "Commit":
        payload = _decode(data)
        if payload.get("type") != "commit":
            raise ObjectError("Invalid commit object")

        return Commit(
            tree=payload["tree"],
            parent=payload["parent"],
            message=payload["message"],
            timestamp=payload["timestamp"],
        )

    @staticmethod
    def create(
        tree_hash: str,
        message: str,
        parent: Optional[str] = None,
    ) -> "Commit":
        return Commit(
            tree=tree_hash,
            parent=parent,
            message=message,
            timestamp=int(time.time()),
        )

    def store(self, store: ObjectStore) -> str:
        return store.store(self.serialize())