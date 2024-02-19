import time


class MemoryIO:
    def __init__(self):
        """
        Initialize an instance of MemoryIO.

        Creates a dictionary to store the session data.
        """

        self.raw_memory_store = {}

    def has_session_id(self, session_id):
        return session_id in self.raw_memory_store

    def has_no_session_id(self, session_id):
        return session_id not in self.raw_memory_store

    def create_store(self, session_id):
        self.raw_memory_store[session_id] = {
            "created_at": int(time.time()),
            "store": {},
        }
        self.save_store(session_id)
        return self.raw_memory_store.get(session_id).get("store")

    def get_store(self, session_id):
        if self.raw_memory_store.get(session_id):
            return self.raw_memory_store.get(session_id).get("store")
        else:
            return None

    def save_store(self, session_id):
        self.get_store(session_id)

    def gc(self):
        if len(self.raw_memory_store) >= 100:  # pragma: no cover
            self.cleanup_old_sessions()

    def cleanup_old_sessions(self):
        current_time = int(time.time())
        sessions_to_delete = [
            session_id
            for session_id, session_info in self.raw_memory_store.items()
            if current_time - session_info["created_at"] > 3600 * 12
        ]
        for session_id in sessions_to_delete:
            del self.raw_memory_store[session_id]
