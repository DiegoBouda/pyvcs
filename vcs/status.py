from pathlib import Path

from .repo import Repository
from .storage import ObjectStore
from .index import Index
from .objects import Blob, Commit, Tree
from .diff import diff_working_vs_index


class Status:
    def __init__(self):
        self.staged: list[Path] = []
        self.modified: list[Path] = []
        self.untracked: list[Path] = []


def _load_commit_tree(repo: Repository) -> dict[Path, str]:
    """
    Load HEAD commit tree into a flat mapping:
    Path -> blob hash
    """
    commit_hash = repo.head_commit()
    if not commit_hash:
        return {}

    store = ObjectStore(repo)
    commit_data = store.load(commit_hash)
    commit = Commit.deserialize(commit_data)

    def walk_tree(tree_hash: str, base: Path, out: dict):
        tree_data = store.load(tree_hash)
        tree = Tree.deserialize(tree_data)
        for name, obj_hash in tree.entries.items():
            path = base / name
            obj_data = store.load(obj_hash)
            try:
                subtree = Tree.deserialize(obj_data)
                walk_tree(obj_hash, path, out)
            except Exception:
                out[path] = obj_hash

    result = {}
    walk_tree(commit.tree, Path("."), result)
    return result


def get_status(repo: Repository) -> Status:
    store = ObjectStore(repo)
    index = Index(repo)
    status = Status()

    head_files = _load_commit_tree(repo)
    index_files = index.entries

    # ---- Staged changes (index vs HEAD)
    for path, blob_hash in index_files.items():
        if path not in head_files:
            status.staged.append(path)
        elif head_files[path] != blob_hash:
            status.staged.append(path)

    # ---- Modified but not staged (working vs index)
    diffs = diff_working_vs_index(repo)
    for d in diffs:
        status.modified.append(d.path)

    # ---- Untracked files
    tracked = set(index_files.keys())
    for path in repo.root.rglob("*"):
        if not path.is_file():
            continue
        if ".pyvcs" in path.parts:
            continue

        rel = path.relative_to(repo.root)
        if rel not in tracked:
            status.untracked.append(rel)

    return status