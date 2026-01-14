from pathlib import Path
from vcs.repo import Repository


def test_repo_init(temp_repo):
    vcs_dir = temp_repo.vcs_dir
    assert vcs_dir.exists()
    assert (vcs_dir / "objects").exists()
    assert (vcs_dir / "refs").exists()


def test_repo_find(temp_repo):
    repo = Repository.find(Path.cwd())
    assert repo.vcs_dir.exists()