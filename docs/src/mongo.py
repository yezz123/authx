import motor.motor_asyncio

from AuthX import Authentication

DATABASE_URL = "mongodb://localhost:27017"
client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
database = client["database_name"]
collection = database["users"]

Authentication.set_database(database)  # motor client
