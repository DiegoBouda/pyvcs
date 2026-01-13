from pathlib import Path
import shutil

from .repo import Repository
from .storage import ObjectStore
from .objects import Blob, Tree
from .index import Index
from .refs import RefError


class CheckoutError(Exception):
    pass


def _restore_tree(repo: Repository, store: ObjectStore, tree_hash: str, target: Path):
    """
    Recursively restore a Tree object into target directory.
    """
    tree_data = store.load(tree_hash)
    tree = Tree.deserialize(tree_data)

    for name, obj_hash in tree.entries.items():
        obj_path = target / name
        # Check if it's a blob or subtree
        obj_data = store.load(obj_hash)
        try:
            subtree = Tree.deserialize(obj_data)
            # It's a Tree
            obj_path.mkdir(exist_ok=True)
            _restore_tree(repo, store, obj_hash, obj_path)
        except Exception:
            # Not a Tree → assume Blob
            blob = Blob.deserialize(obj_data)
            obj_path.parent.mkdir(parents=True, exist_ok=True)
            obj_path.write_bytes(blob.data)


def checkout_branch(repo: Repository, branch_name: str):
    """
    Switch to a branch:
    - Updates HEAD
    - Restores working directory from commit tree
    """
    from .refs import checkout as update_head

    update_head(repo, branch_name)

    commit_hash = repo.head_commit()
    if not commit_hash:
        return  # empty branch, nothing to restore

    store = ObjectStore(repo)
    commit_data = store.load(commit_hash)
    from .objects import Commit

    commit = Commit.deserialize(commit_data)
    root_tree_hash = commit.tree

    # Clear working directory (except .pyvcs)
    for item in repo.root.iterdir():
        if item.name == ".pyvcs":
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    # Restore tree
    _restore_tree(repo, store, root_tree_hash, repo.root)


def checkout_commit(repo: Repository, commit_hash: str):
    """
    Checkout a specific commit (detached HEAD).
    Currently updates files only; does not change symbolic HEAD.
    """
    store = ObjectStore(repo)
    commit_data = store.load(commit_hash)
    from .objects import Commit

    commit = Commit.deserialize(commit_data)
    root_tree_hash = commit.tree

    # Clear working directory (except .pyvcs)
    for item in repo.root.iterdir():
        if item.name == ".pyvcs":
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    # Restore tree
    _restore_tree(repo, store, root_tree_hash, repo.root)