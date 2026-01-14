from pathlib import Path
from vcs.storage import ObjectStore
from vcs.index import Index
from vcs.commit import create_commit


def test_commit_creation(temp_repo):
    file = Path("a.txt")
    file.write_text("content")

    store = ObjectStore(temp_repo)
    index = Index(temp_repo)

    index.add(file, store)
    commit_hash = create_commit(temp_repo, "initial commit")

    assert commit_hash is not None