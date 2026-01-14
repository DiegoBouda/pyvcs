from pathlib import Path
from vcs.refs import create_branch
from vcs.checkout import checkout_branch


def test_branch_checkout(temp_repo):
    Path("file.txt").write_text("main")

    from vcs.storage import ObjectStore
    from vcs.index import Index
    from vcs.commit import create_commit

    store = ObjectStore(temp_repo)
    index = Index(temp_repo)

    index.add(Path("file.txt"), store)
    create_commit(temp_repo, "main commit")

    create_branch(temp_repo, "feature")
    checkout_branch(temp_repo, "feature")

    assert temp_repo.current_branch() == "feature"