from time import time

import pytest

from authx._internal import MemoryIO


@pytest.fixture
def memory_io():
    return MemoryIO()


@pytest.mark.asyncio
async def test_create_store(memory_io):
    session_id = "123"
    store = await memory_io.create_store(session_id)
    assert store == {}
    assert memory_io.raw_memory_store[session_id]["store"] == {}


@pytest.mark.asyncio
async def test_get_store_existing(memory_io):
    session_id = "123"
    memory_io.raw_memory_store[session_id] = {
        "created_at": int(time()),
        "store": {"key": "value"},
    }
    store = await memory_io.get_store(session_id)
    assert store == {"key": "value"}


@pytest.mark.asyncio
async def test_get_store_nonexistent(memory_io):
    session_id = "123"
    store = await memory_io.get_store(session_id)
    assert store is None


@pytest.mark.asyncio
async def test_save_store(memory_io):
    session_id = "123"
    memory_io.raw_memory_store[session_id] = {
        "created_at": int(time()),
        "store": {"key": "value"},
    }
    await memory_io.save_store(session_id)
    assert await memory_io.get_store(session_id) == {"key": "value"}


@pytest.mark.asyncio
async def test_cleanup_old_sessions(memory_io):
    current_time = int(time())
    memory_io.raw_memory_store = {
        "1": {"created_at": current_time - 3600 * 12 - 1, "store": {}},
        "2": {"created_at": current_time - 3600 * 12, "store": {}},
        "3": {"created_at": current_time - 3600 * 12 + 1, "store": {}},
    }
    await memory_io.cleanup_old_sessions()
    expected_output = {
        "2": {"created_at": current_time - 3600 * 12, "store": {}},
        "3": {"created_at": current_time - 3600 * 12 + 1, "store": {}},
    }
    assert memory_io.raw_memory_store == expected_output


@pytest.mark.asyncio
async def test_has_session_id():
    store = MemoryIO()
    await store.create_store("test-id")
    assert await store.has_session_id("test-id")
    assert not await store.has_no_session_id("test-id")


@pytest.mark.asyncio
async def test_get_store():
    store = MemoryIO()
    await store.create_store("test-id")
    assert await store.get_store("test-id") == {}
    assert await store.get_store("nonexistent-id") is None


@pytest.mark.asyncio
async def populate_old_sessions(memory_io, count, created_at):
    for i in range(count):
        memory_io.raw_memory_store[str(i)] = {
            "created_at": created_at,
            "store": {},
        }


@pytest.mark.asyncio
async def test_gc_cleanup_old_sessions(memory_io):
    # Populate raw_memory_store with 100 sessions older than 12 hours
    current_time = int(time())
    twelve_hours_ago = current_time - 3600 * 12
    await populate_old_sessions(memory_io, 100, twelve_hours_ago)

    # Add one more session within 12 hours
    extra_session_id = "1000"
    memory_io.raw_memory_store[extra_session_id] = {
        "created_at": current_time,
        "store": {},
    }

    # Ensure gc triggers cleanup
    await memory_io.gc()

    # Ensure old sessions are cleaned up
    assert len(memory_io.raw_memory_store) == 101
    assert extra_session_id in memory_io.raw_memory_store
