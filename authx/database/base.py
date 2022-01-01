from typing import Iterable, Optional, Union
from uuid import UUID


class BaseDBBackend:
    async def get(self, id: Union[int, UUID]) -> Optional[dict]:
        raise NotImplementedError

    async def get_by_email(self, email: str) -> Optional[dict]:
        raise NotImplementedError()

    async def get_by_username(self, username: str) -> Optional[dict]:
        raise NotImplementedError()

    async def get_by_social(self, provider: str, sid: str) -> Optional[dict]:
        raise NotImplementedError()

    async def create(self, obj: dict) -> Union[int, UUID]:
        raise NotImplementedError()

    async def update(self, id: Union[int, UUID], obj: dict) -> bool:
        raise NotImplementedError()

    async def delete(self, id: Union[int, UUID]) -> bool:
        raise NotImplementedError()

    async def count(self, query: Optional[dict] = None) -> int:
        raise NotImplementedError()

    async def request_email_confirmation(self, email: str, token_hash: str) -> None:
        raise NotImplementedError()

    async def confirm_email(self, token_hash: str) -> bool:
        raise NotImplementedError()

    async def get_blacklist(self) -> Iterable[dict]:
        raise NotImplementedError()

    async def search(self, f: dict, p: int, size: int) -> tuple[dict, int]:
        raise NotImplementedError()
