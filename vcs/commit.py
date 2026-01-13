from pathlib import Path
from typing import Dict

from .repo import Repository, RepositoryError
from .storage import ObjectStore
from .objects import Tree, Commit
from .index import Index


class CommitError(Exception):
    pass


def _build_tree(entries: Dict[str, str], store: ObjectStore) -> str:
    """
    Build nested Tree objects from index entries and return root tree hash.
    entries: { "dir/file.txt": blob_hash }
    """
    tree_map: Dict[str, dict] = {}

    # Build nested dict structure
    for path, blob_hash in entries.items():
        parts = path.split("/")
        current = tree_map
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = blob_hash

    def write_tree(node: dict) -> str:
        tree_entries = {}
        for name, value in node.items():
            if isinstance(value, dict):
                subtree_hash = write_tree(value)
                tree_entries[name] = subtree_hash
            else:
                tree_entries[name] = value

        tree = Tree(tree_entries)
        return tree.store(store)

    return write_tree(tree_map)


def create_commit(
    repo: Repository,
    message: str,
) -> str:
    """
    Create a commit from the current index and update HEAD.
    Returns the new commit hash.
    """
    index = Index(repo)
    store = ObjectStore(repo)

    if not index.entries:
        raise CommitError("Nothing to commit")

    # Build tree from index
    root_tree_hash = _build_tree(index.entries, store)

    # Get parent commit (if any)
    parent = repo.head_commit()

    # Create and store commit
    commit = Commit.create(
        tree_hash=root_tree_hash,
        message=message,
        parent=parent,
    )
    commit_hash = commit.store(store)

    # Update current branch reference
    ref_path = repo.head_ref_path()
    ref_path.write_text(commit_hash)

    # Clear staging area
    index.clear()

    return commit_hash