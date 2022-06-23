# Admin

the Main Class `AdminService` is the main class that is used to perform all
admins operations.

```py
from authx import AdminService, UsersRepo, BaseDBBackend, RedisBackend

admin = AdminService(
    repo = UsersRepo(
        database =  BaseDBBackend(
            host = "localhost",
            port = 3306,
            user = "root",
            password = "",
            database = "authx",
        ),
        cache = RedisBackend(
            host = "localhost",
            port = 6379,
            ),
        callbacks = [],
)
)
```
