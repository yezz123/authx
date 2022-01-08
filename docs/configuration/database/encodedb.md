# EncodeDB

Encode Database is a database that gives you simple `asyncio` support for a range of databases.

It allows you to make queries using the powerful `SQLAlchemy Core` expression language and provides support for `PostgreSQL`, `MySQL`, and `SQLite`.

Databases is suitable for integrating against any async Web framework, such as `Starlette`, `Sanic`, `Responder`, `Quart`, `aiohttp`, `Tornado`, or `FastAPI`.

You could check the [documentation](https://www.encode.io/databases/) for more information.

- Check that you install requirements:

```shell
pip install authx[encodedb]
```

Setup the database, and we will use the `EncodeDBBackend` as a dependency.

```py
import databases
from authx import Authentication, EncodeDBBackend

auth = Authentication(
    backend=EncodeDBBackend(
        database=databases(
            host="localhost",
            port=5432,
            user="postgres",
            password="postgres",
            database="authx",
        ),
    )
)
```

Here we present a simple PostgreSQL database example on how to use the `EncodeDBBackend`.

### Create/Update/Delete Functions

Here we are creating the functions that will be used to create and update the database,based on the request.

- Create:

```py
async def create(self, obj: dict) -> UUID:
    uuid = uuid4()
    obj[id] = uuid
    query = self.users.insert()
    await self.database.execute(query=query, values=obj)
    return uuid
```

- Update:

```py
 async def update(self, id: UUID, obj: dict) -> bool:
    obj.pop("id", None)
    query = (
        sa.update(self.users)
        .where(self.users.c.id == id)
        .values(obj)
        .returning(self.users.c.id)
    )
    res = await self.database.execute(query)
    return bool(res)
```

- Delete:

```py
async def delete(self, id: UUID) -> bool:
    query = (
        sa.delete(self.users)
        .where(self.users.c.id == id)
        .returning(self.users.c.id)
    )
    res = await self.database.execute(query)
    return bool(res)
```

### Complex Functions

After you have created the database, you can use the following functions to create, update, and delete users.

- request Email Confirmation:

```py
async def request_email_confirmation(self, email: str, token_hash: str) -> None:
    query = (
        pg_insert(self.email_confirmations)
        .values(email=email, token=token_hash)
        .on_conflict_do_update(constraint="email", set_={"token": token_hash})
    )
    await self.database.execute(query)
    return None
```

- Confirm Email:

```py
async def confirm_email(self, token_hash: str) -> bool:
    query = sa.select(self.email_confirmations).where(
        self.email_confirmations.c.token == token_hash
    )
    email_confirmation = await self.database.fetch_one(query)
    if email_confirmation:
        email = email_confirmation["email"]
        async with self.database.transaction():
            query = (
                sa.update(self.users)
                .where(self.users.c.email == email)
                .values(confirmed=True)
            )
            await self.database.execute(query)
            query = sa.delete(self.email_confirmations).where(
                self.email_confirmations.c.email == email
            )
            await self.database.execute(query)
        return True
    else:
        return False
```

Here we Present different functions to create, update, and delete users, also some complex functions to use it if you would like to extend the functionality.