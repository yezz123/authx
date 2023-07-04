from authx._internal import MemoryIO


def test_has_session_id():
    store = MemoryIO()
    store.create_store("test-id")
    assert store.has_session_id("test-id")
    assert not store.has_no_session_id("test-id")


def test_get_store():
    store = MemoryIO()
    store.create_store("test-id")
    assert store.get_store("test-id") == {}
    assert store.get_store("nonexistent-id") is None
