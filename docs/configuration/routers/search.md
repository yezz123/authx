# Search Router

The Search router will generate a set of endpoints for Searching users.

- GET `/get_user`
- GET `/search`

## Setup the Search Router

To Setup the Search service, you will need to add all requirements to the object
`SearchService`.

```py
from typing import Callable, Optional
from authx.services.search import SearchService
from authx.api import UsersRepo

SearchService.setup(
        repo = UserRepo,
        admin_required = Callable
    )
```

This one gonna help use to use the Search service, that we provide.

```py
from authx import Authentication
from fastapi import FastAPI

app = FastAPI()
auth = Authentication()

app.include_router(auth.search_router, prefix="/api/users")
```

### Get User

As the name suggests, we gonna use the `GET` method to get a user using his ID
that will return the User Data.

```py
@router.get("/{id}", name="auth:get_user", dependencies=[Depends(admin_required)])
async def get_user(id: int):
    service = SearchService()
    return await service.get_user(id)
```

The `service.get_user` function work to return the User Data, but also could
raise an `HTTPException` if the User is not found.

```py
    async def get_user(self, id: int):
        item = await self._repo.get(id)
        if item is None:
            raise HTTPException(404)

        return UserPrivateInfo(**item).dict(by_alias=True)
```

### Search

This route will return a list of users that match the search query. Using the
`GET` method, you can pass the `p` parameter to search for users.

```py
@router.get("", name="auth:search", dependencies=[Depends(admin_required)])
    async def search(
        *, id: Optional[int] = None, username: Optional[str] = None, p: int = 1
    ):
        service = SearchService()
        return await service.search(id, username, p)

    return router
```

As always, we have the function `service.search` that will return a list of
users that match the search query. With this argument, you can search for users
by ID, username or both.

- `id`: The ID of the user.
- `username`: The username of the user.
- `p`: The page number.

!!! info

        The P parameter is used to paginate the results. (`PAGE_SIZE = 20`)

```py
async def search(
    self, id: Optional[int],
    username: Optional[str], p: int) -> dict:
            PAGE_SIZE = 20
            items, count = await self._repo.search(id, username, p, PAGE_SIZE)
            div = count // PAGE_SIZE
            pages = div if count % PAGE_SIZE == 0 else div + 1
    return {
            "items": [
                UserPrivateInfo(**item).dict(by_alias=True, exclude_none=True)
                for item in items
            ],
            "pages": pages,
            "currentPage": p,
    }
```
