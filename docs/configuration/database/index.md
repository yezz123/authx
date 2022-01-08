# Database

AuthX provide a simple way to create a database, and a simple way to create a database crud in both SQL Databases and NoSQL Databases.

Right Now we Support the following Databases:

- [x] SQL Databases:
    - [x] MySQL
    - [x] PostgreSQL
    - [x] SQLite
- [x] NoSQL Databases:
    - [x] MongoDB

In the future, we will add more databases, but right now we support only the most common ones.

Even that Most Of Functionality work also without using Database at all. `BaseDBBackend`.

## Operations

All the operations are async functions, and they are going to return a boolean, and the boolean is going to be True if the operation was successful, and False if not.

Thats why when we will be using the Normal Dependency Injection, we will add only the `BaseDBBackend` as a dependency, and we will use the `Database` as a dependency.

```py
from fastapi import FastAPI
from starlette.config import Config
from authx import Authentication, User, BaseDBBackend

app = FastAPI()
auth = Authentication(database_backend=BaseDBBackend)
```

## Database Support

- [x] [SQL Database](encodedb.md).
- [x] [NoSQL Database](mongodb.md).