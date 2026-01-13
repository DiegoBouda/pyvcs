from pathlib import Path
from typing import List

from .repo import Repository, RepositoryError


class RefError(Exception):
    pass


def list_branches(repo: Repository) -> List[str]:
    """
    Return all branch names in the repository.
    """
    heads_dir = repo.heads_dir
    return [p.name for p in heads_dir.iterdir() if p.is_file()]


def create_branch(repo: Repository, branch_name: str) -> None:
    """
    Create a new branch pointing to the current HEAD commit.
    """
    ref_path = repo.heads_dir / branch_name
    if ref_path.exists():
        raise RefError(f"Branch '{branch_name}' already exists")

    current_commit = repo.head_commit() or ""
    ref_path.write_text(current_commit)


def delete_branch(repo: Repository, branch_name: str) -> None:
    """
    Delete a branch.
    """
    if branch_name == repo.current_branch():
        raise RefError("Cannot delete current branch")

    ref_path = repo.heads_dir / branch_name
    if not ref_path.exists():
        raise RefError(f"Branch '{branch_name}' does not exist")

    ref_path.unlink()


def checkout(repo: Repository, branch_name: str) -> None:
    """
    Switch HEAD to the given branch.
    Does not modify working directory contents (you would do that in CLI later).
    """
    ref_path = repo.heads_dir / branch_name
    if not ref_path.exists():
        raise RefError(f"Branch '{branch_name}' does not exist")

    # Update HEAD to point to the branch
    repo.head_file.write_text(f"refs/heads/{branch_name}")