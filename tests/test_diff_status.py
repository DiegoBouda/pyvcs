from pathlib import Path
from vcs.diff import diff_working_vs_index
from vcs.status import get_status
from vcs.storage import ObjectStore
from vcs.index import Index
from vcs.commit import create_commit


def test_diff_and_status(temp_repo):
    file = Path("file.txt")
    file.write_text("hello")

    store = ObjectStore(temp_repo)
    index = Index(temp_repo)

    index.add(file, store)
    create_commit(temp_repo, "initial")

    index.add(file, store)
    file.write_text("hello world")

    diffs = diff_working_vs_index(temp_repo)
    assert len(diffs) == 1

    status = get_status(temp_repo)
    assert "file.txt" in status.modified