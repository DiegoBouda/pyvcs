from vcs.storage import ObjectStore


def test_object_store_roundtrip(temp_repo):
    store = ObjectStore(temp_repo)

    data = b"hello world"
    obj_hash = store.store(data)

    loaded = store.load(obj_hash)
    assert loaded == data