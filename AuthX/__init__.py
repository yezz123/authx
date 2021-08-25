__version__ = "0.0.1"

from typing import Iterable, Optional

from aioredis import Redis
from fastapi import APIRouter, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorClient

from AuthX.api import UsersRepo
from AuthX.core.jwt import JWTBackend
from AuthX.core.user import User
from AuthX.database import MongoDBBackend, RedisBackend
from AuthX.routers import (
    get_admin_router,
    get_auth_router,
    get_password_router,
    get_search_router,
    get_social_router,
)
