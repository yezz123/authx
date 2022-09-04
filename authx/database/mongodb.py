from typing import Iterable, Optional, Tuple

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)
from pymongo import ReturnDocument

from authx.database import BaseDBBackend


class MongoDBBackend(BaseDBBackend):
    """Setup Database for authx using MongoDB & Motor"""

    def __init__(self, client: AsyncIOMotorClient, database_name: str = "test") -> None:
        self._client = client
        self._database_name = database_name
        self.init()

    def init(self) -> None:
        self._db: AsyncIOMotorDatabase = self._client[self._database_name]
        self._users: AsyncIOMotorCollection = self._db["users"]
        self._email_confirmations: AsyncIOMotorCollection = self._db[
            "email_confirmations"
        ]
        self._counters: AsyncIOMotorCollection = self._db["counters"]

        self._settings: AsyncIOMotorCollection = self._db["settings"]

    async def _increment_id(self) -> int:
        ret = await self._counters.find_one_and_update(
            {"name": "users"},
            {"$inc": {"c": 1}},
            return_document=ReturnDocument.AFTER,
        )
        return ret.get("c")

    async def get(self, id: int) -> Optional[dict]:
        return await self._users.find_one({"id": id}, {"_id": 0})

    async def get_by_email(self, email: str) -> Optional[dict]:
        return await self._users.find_one({"email": email}, {"_id": 0})

    async def get_by_username(self, username: str) -> Optional[dict]:
        return await self._users.find_one({"username": username}, {"_id": 0})

    async def get_by_social(self, provider: str, sid: str) -> Optional[dict]:
        return await self._users.find_one(
            {"provider": provider, "sid": sid}, {"_id": 0}
        )

    async def create(self, obj: dict) -> int:
        async with await self._client.start_session() as session:
            async with session.start_transaction():
                id = await self._increment_id()
                obj["id"] = id
                await self._users.insert_one(obj)
        return id

    async def update(self, id: int, obj: dict) -> bool:
        res = await self._users.update_one({"id": id}, {"$set": obj})
        return bool(res.matched_count)

    async def delete(self, id: int) -> bool:
        res = await self._users.delete_one({"id": id})
        return bool(res.deleted_count)

    async def count(self, query: Optional[dict] = None) -> int:
        return await self._users.count_documents(query)

    async def request_email_confirmation(self, email: str, token_hash: str) -> None:
        await self._email_confirmations.update_one(
            {"email": email}, {"$set": {"token": token_hash}}, upsert=True
        )
        return None

    async def confirm_email(self, token_hash: str) -> bool:
        ec = await self._email_confirmations.find_one({"token": token_hash})
        if ec is not None:
            email = ec.get("email")
            async with await self._client.start_session() as session:
                async with session.start_transaction():
                    await self._users.update_one(
                        {"email": email}, {"$set": {"confirmed": True}}
                    )
                    await self._email_confirmations.delete_many({"email": email})
            return True
        else:
            return False

    async def get_blacklist(self) -> Iterable[dict]:
        return await self._users.find({"active": False}, {"_id": 0}).to_list(None)

    async def search(self, f: dict, p: int, size: int) -> Tuple[dict, int]:
        count = await self._users.count_documents(f)
        items = (
            await self._users.find(f, {"_id": 0})
            .skip((p - 1) * size)
            .limit(size)
            .to_list(None)
        )
        return items, count
