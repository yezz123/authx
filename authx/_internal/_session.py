"""Session management utilities for AuthX."""

import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from authx._internal._utils import get_now, get_uuid


class SessionInfo(BaseModel):
    """Represents an active authentication session.

    Usable as a FastAPI ``response_model`` for session listing endpoints.
    """

    session_id: str = Field(default_factory=get_uuid)
    uid: str
    created_at: datetime.datetime = Field(default_factory=get_now)
    last_active: datetime.datetime = Field(default_factory=get_now)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_info: Optional[dict[str, Any]] = None
    is_active: bool = True


class InMemorySessionStore:
    """In-memory session store for development and single-process deployments.

    For production multi-worker setups, implement the ``SessionStoreProtocol``
    from ``authx.types`` with Redis or a database backend.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, SessionInfo] = {}

    async def create(self, session: SessionInfo) -> None:
        self._sessions[session.session_id] = session

    async def get(self, session_id: str) -> Optional[SessionInfo]:
        return self._sessions.get(session_id)

    async def update(self, session_id: str, **kwargs: Any) -> None:
        session = self._sessions.get(session_id)
        if session is not None:
            for key, value in kwargs.items():
                if hasattr(session, key):
                    object.__setattr__(session, key, value)

    async def delete(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    async def list_by_user(self, uid: str) -> list[SessionInfo]:
        return [s for s in self._sessions.values() if s.uid == uid and s.is_active]

    async def delete_all_by_user(self, uid: str) -> None:
        to_remove = [sid for sid, s in self._sessions.items() if s.uid == uid]
        for sid in to_remove:
            del self._sessions[sid]
