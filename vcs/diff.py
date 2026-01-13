from pathlib import Path
import difflib

from .repo import Repository
from .storage import ObjectStore
from .index import Index
from .objects import Blob


class DiffEntry:
    def __init__(self, path: Path, diff: str):
        self.path = path
        self.diff = diff


def _read_working_file(path: Path) -> bytes:
    if not path.exists() or not path.is_file():
        return b""
    return path.read_bytes()


def diff_working_vs_index(repo: Repository) -> list[DiffEntry]:
    """
    Compare working directory files against staged (index) versions.
    Returns a list of DiffEntry.
    """
    store = ObjectStore(repo)
    index = Index(repo)
    diffs = []

    for rel_path, blob_hash in index.entries.items():
        abs_path = repo.root / rel_path

        # Load staged blob
        staged_data = store.load(blob_hash)
        staged_blob = Blob.deserialize(staged_data)

        # Load working file
        working_data = _read_working_file(abs_path)

        if working_data == staged_blob.data:
            continue  # no change

        staged_lines = staged_blob.data.decode(errors="ignore").splitlines(keepends=True)
        working_lines = working_data.decode(errors="ignore").splitlines(keepends=True)

        diff_text = "".join(
            difflib.unified_diff(
                staged_lines,
                working_lines,
                fromfile=f"a/{rel_path}",
                tofile=f"b/{rel_path}",
            )
        )

        diffs.append(DiffEntry(rel_path, diff_text))

    return diffs