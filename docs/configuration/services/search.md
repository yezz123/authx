# Search

the Main Class `SearchService` is the main class that is used to perform all
search operations.

```py
from authx import SearchService, UsersRepo, BaseDBBackend, RedisBackend

search = SearchService(
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
