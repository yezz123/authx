## MongoDB Provider

### Initial and Setup Class

As we know that the database provider is the most important part of the configuration, we will start with the initial and setup class.

using [MongoDB/Motor](https://motor.readthedocs.io/en/stable/) as an Asynchronous Driver.

```py

class MongoDBBackend:
    def __init__(self, database_name: str = "test") -> None:
        self._database_name = database_name

    def set_client(self, client: AsyncIOMotorClient) -> None:
        self._client = client
        self.init()

    def init(self) -> None:
        self._db: AsyncIOMotorDatabase = self._client[self._database_name]
        self._users: AsyncIOMotorCollection = self._db["users"]
        self._email_confirmations: AsyncIOMotorCollection = self._db[
            "email_confirmations"
        ]
        self._counters: AsyncIOMotorCollection = self._db["counters"]

        self._settings: AsyncIOMotorCollection = self._db["settings"]
```

Here we are initializing the database, and assigning the collections to the database, also adding a counter collection, with a default settings.

### Create/Update/Delete Functions

Here we are creating the functions that will be used to create and update the database,based on the request.

```py
    async def create(self, obj: dict) -> int:
        async with await self._client.start_session() as session:
            async with session.start_transaction():
                id = await self._increment_id()
                obj.update({"id": id})
                await self._users.insert_one(obj)
        return id
```

Here we give the user a unique id, and then we insert the user into the database [Based on the Models](../models/index.md).

For the update function, we are using the same logic, but we are updating the user instead of inserting it, as an argument, we give the ID, and the object, this gonna return a boolean.

```py
async def update(self, id: int, obj: dict) -> bool:
        res = await self._users.update_one({"id": id}, {"$set": obj})
        return bool(res.matched_count)
```

To Delete a user we just give the ID as an argument, and return a boolean.

```py
async def delete(self, id: int) -> bool:
        res = await self._users.delete_one({"id": id})
        return bool(res.deleted_count)
```

### Complex Functions

After Creating the Database Cruds, we are going to create the functions that will be used to verify the email, and confirm the email to let the user, use the application.

As we know we need the `email:str`, a hashed token also to request the email confirmation.

```py
async def request_email_confirmation(self, email: str, token_hash: str) -> None:
        await self._email_confirmations.update_one(
            {"email": email}, {"$set": {"token": token_hash}}, upsert=True)
        return None
```

This gonna return the request with a token to confirm the email.

```py
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
```

There is a lot of functions for example:

* `count`: Count the number of users in the database.
* `get_blacklist`: Get the blacklist of the users.
