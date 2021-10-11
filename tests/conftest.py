import asyncio

import pytest


@pytest.fixture
def event_loop():
    """
    Fixture for the event loop.

    Yields:
        asyncio.AbstractEventLoop: The event loop.
    """
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
