import motor.motor_asyncio
from decouple import config

mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
    config("MONGO_URI", default="mongodb://localhost:27017/")
)
db = mongo_client[config("MONGO_DB", default="authx")]
collection = db[config("MONGO_COLLECTION", default="users")]
