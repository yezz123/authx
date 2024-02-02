from time import time

import pytest

from authx._internal import MemoryIO


@pytest.fixture
def memory_io():
    return MemoryIO()


def test_create_store(memory_io):
    session_id = "123"
    store = memory_io.create_store(session_id)
    assert store == {}
    assert memory_io.raw_memory_store[session_id]["store"] == {}


def test_get_store_existing(memory_io):
    session_id = "123"
    memory_io.raw_memory_store[session_id] = {
        "created_at": int(time()),
        "store": {"key": "value"},
    }
    store = memory_io.get_store(session_id)
    assert store == {"key": "value"}


def test_get_store_nonexistent(memory_io):
    session_id = "123"
    store = memory_io.get_store(session_id)
    assert store is None


def test_save_store(memory_io):
    session_id = "123"
    memory_io.raw_memory_store[session_id] = {
        "created_at": int(time()),
        "store": {"key": "value"},
    }
    memory_io.save_store(session_id)
    assert memory_io.get_store(session_id) == {"key": "value"}


def test_cleanup_old_sessions(memory_io):
    current_time = int(time())
    memory_io.raw_memory_store = {
        "1": {"created_at": current_time - 3600 * 12 - 1, "store": {}},
        "2": {"created_at": current_time - 3600 * 12, "store": {}},
        "3": {"created_at": current_time - 3600 * 12 + 1, "store": {}},
    }
    memory_io.cleanup_old_sessions()
    expected_output = {
        "2": {"created_at": current_time - 3600 * 12, "store": {}},
        "3": {"created_at": current_time - 3600 * 12 + 1, "store": {}},
    }
    assert memory_io.raw_memory_store == expected_output


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
