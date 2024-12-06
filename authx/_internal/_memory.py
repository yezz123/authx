import asyncio
import time
from typing import Dict, Any, Optional


class MemoryIO:
    raw_memory_store: Dict[str, Dict[str, Any]]

    """
    MemoryIO is a class that implements the IO interface for the session store.

    It is used to store session data in memory.
    """

    def __init__(self) -> None:
        """
        Initialize an instance of MemoryIO.

        Creates a dictionary to store the session data.
        """
        self.raw_memory_store = {}

    async def has_session_id(self, session_id: str) -> bool:
        return session_id in self.raw_memory_store

    async def has_no_session_id(self, session_id: str) -> bool:
        return session_id not in self.raw_memory_store

    async def create_store(self, session_id: str) -> Dict[str, Any]:
        self.raw_memory_store[session_id] = {
            "created_at": int(time.time()),
            "store": {},
        }
        await self.save_store(session_id)
        return self.raw_memory_store.get(session_id, {}).get("store", {})

    async def get_store(self, session_id: str) -> Optional[Dict[str, Any]]:
        if self.raw_memory_store.get(session_id):
            return self.raw_memory_store.get(session_id, {}).get("store")
        else:
            return None

    async def save_store(self, session_id: str) -> None:
        await self.get_store(session_id)

    async def gc(self) -> None:
        if len(self.raw_memory_store) >= 100:
            await self.cleanup_old_sessions()

    async def cleanup_old_sessions(self) -> None:
        current_time = int(time.time())
        sessions_to_delete = [
            session_id
            for session_id, session_info in self.raw_memory_store.items()
            if current_time - session_info["created_at"] > 3600 * 12
        ]
        for session_id in sessions_to_delete:
            del self.raw_memory_store[session_id]
