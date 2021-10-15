# Administration Router

The Admin router will generate a set of endpoints for Administration permissions.

* GET `/get_blacklist`
* POST `/toggle_blacklist`
* GET `/get_blackout`
* POST `/set_blackout`
* DELETE `/delete_blackout`
* GET `/get_id_by_username`
* POST `/kick`

## Setup The Administration Router

To Setup the Admin service, you will need to add all requirements to the object `get_router`.

```py
def get_router(
    repo: UsersRepo,
    admin_required: Callable
):
AdminService.setup(repo)
```

This one gonna help use to use the setup repository and the `admin_required`.

Let's Provide the `admin_router`:

```py
from AuthX import Authentication
from fastapi import FastAPI

app = FastAPI()
auth = Authentication()

app.include_router(auth.admin_router, prefix="/api/users")
```

### Get Blacklist

As we know we will use the `GET` mehtod to get the blacklist, so we will need to create a endpoint for this.

```py
@router.get(
        "/blacklist",
        name="admin:get_blacklist",
        dependencies=[Depends(admin_required)]
    )
    async def get_blacklist():
        service = AdminService()
        return await service.get_blacklist()
```

The `service.get_blacklist()` method will return a list of usernames that are blacklisted.

```py
async def get_blacklist(self) -> dict:
    return await self._repo.get_blacklist()
```

This one is based on `UsersManagementMixin` where we create a function that will return a list of usernames that are blacklisted.

### Toggle Blacklist

As we know we will use the `POST` mehtod to toggle the blacklist, so we will need to create a endpoint for this.

```py
@router.post(
        "/{id}/blacklist",
        name="admin:toggle_blacklist",
        dependencies=[Depends(admin_required)],
    )
    async def toggle_blacklist(*, id: int):
        service = AdminService()
        return await service.toggle_blacklist(id)
```

The `service.toggle_blacklist(id)` method will toggle the blacklist of the user with the given id.

```py
async def toggle_blacklist(self, id: int) -> None:
    return await self._repo.toggle_blacklist(id)
```

This one also is based on `UsersManagementMixin` where we create a function that will toggle the blacklist of the user with the given id.

### Get Blackout

As we know we will use the `GET` mehtod to get the blackout, so we will need to create a endpoint for this.

```py
@router.get(
        "/blackout",
        name="admin:get_blackout",
        dependencies=[Depends(admin_required)]
    )
    async def get_blackout():
        service = AdminService()
        return await service.get_blackout()
```

The `service.get_blackout()` method will return a list of usernames that are blacklisted, if an error it will raise an exception (404).

This one is based on `UsersManagementMixin`, but it return data from `redis` cache that why __take Care__, and Configure your [redis](https://redis.io/) server.

### Set Blackout

The `POST` mehtod to set the blackout, this one gonna set the blackout for the user with the given id.

```py
@router.post(
        "/blackout",
        name="admin:set_blackout",
        dependencies=[Depends(admin_required)]
    )
    async def set_blackout():
        service = AdminService()
        return await service.set_blackout()
```

Back to `service.set_blackout()` method, we will need to get the `id` from the request, and the `time` from the request.

```py
async def set_blackout(self) -> None:
    epoch = datetime.utcfromtimestamp(0)
    ts = int((datetime.utcnow() - epoch).total_seconds()) + 10
    await self._repo.set_blackout(ts)
    return None
```

the `_repo.set_blackout(ts)` set the `ts` to the `redis` cache.

### Delete Blackout

The `DELETE` mehtod to delete the blackout, this one gonna delete the blackout for the user with the given id.

```py
@router.delete(
        "/blackout",
        name="admin:delete_blackout",
        dependencies=[Depends(admin_required)],
    )
    async def delete_blackout():
        service = AdminService()
        return await service.delete_blackout()
```

Now we could take a look at the `service.delete_blackout()` method.

```py
async def delete_blackout(self) -> None:
    await self._repo.delete_blackout()
```

At this point, the blackout will be deleted from the `redis` cache.

!!! info
    All of this is set on `redis` cache, so you need to configure your [redis](https://redis.io/) server.

### Get ID By Username

Now, after we finish the Blacklist and Blackout, we will need to create a endpoint to get the id of the user with the given username.

```py
@router.get(
        "/id_by_username",
        name="admin:get_id_by_username",
        dependencies=[Depends(admin_required)],
    )
    async def get_id_by_username(*, username: str):
        service = AdminService()
        return await service.get_id_by_username(username)
```

Now to understand how this one works, we will need to create a function that will return the id of the user with the given username, and this is `service.get_id_by_username(username)` method.

```py
async def get_id_by_username(self, username: str) -> Optional[dict]:
    item = await self._repo.get_by_username(username)
    return {"id": item.get("id")}
```

We get the username from database, and if it is not found, we will return `None`.

### Kick

For the kick, we will need to create a endpoint to kick the user with the given id, this router need a `POST` method.

```py
@router.post(
        "/{id}/kick",
        name="admin:kick",
        dependencies=[Depends(admin_required)]
    )
    async def kick(*, id: int):
        service = AdminService()
        return await service.kick(id)
```

As we see, we will need to get the id from the request, and then we will call the `service.kick(id)` method.

```py
async def kick(self, id: int) -> None:
    await self._repo.kick(id)
```

And this will kick the user with the given id, but need to take care, if the user is not found, we will raise an exception (404).

Also, this need the Key relate to cache, and the `_access_expiration` is the time that the user will be kicked.

!!! Warning
    Configure your [redis](https://redis.io/) server, or check this [redis Configuration](../cache/index.md).
