from typing import Optional
from uuid import UUID, uuid4

import prisma

from authx.database import BaseDBBackend


class PrismaDBBackend(BaseDBBackend):
    """
    Setup Database for authx using Prisma Python Client
    """

    def __init__(self, database: prisma.Client) -> None:
        self.database = database

    async def get(self, id: UUID) -> Optional[dict]:
        query = self.database.user(id=id)
        return await query.execute()

    async def get_by_email(self, email: str) -> Optional[dict]:
        query = self.database.user.find_one(email=email)
        return await query.execute()

    async def get_by_username(self, username: str) -> Optional[dict]:
        query = self.database.user.find_one(username=username)
        return await query.execute()

    async def get_by_social(self, provider: str, sid: str) -> Optional[dict]:
        query = self.database.user.find_one(
            provider=provider,
            social_id=sid,
        )
        return await query.execute()

    async def create(self, obj: dict) -> UUID:
        uuid = uuid4()
        obj["id"] = uuid
        query = self.database.create_user(data=obj)
        return await query.execute()

    async def update(self, id: UUID, obj: dict) -> bool:
        obj.pop("id", None)

        query = self.database.update_user(
            data=obj,
            where=self.database.user.id == id,
        )
        return await query.execute()
