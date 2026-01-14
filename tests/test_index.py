from pathlib import Path
from vcs.index import Index
from vcs.storage import ObjectStore


def test_index_add(temp_repo):
    file = Path("file.txt")
    file.write_text("hello")

    store = ObjectStore(temp_repo)
    index = Index(temp_repo)

    index.add(file, store)

    assert "file.txt" in index.entries