# Dependency Injection

In line with FastAPI's dependency injection syntax, AuthX dependencies can be utilized in multiple scenarios.

## Route Protection

A straightforward application involves protecting a specific route, such as `GET /protected`.

If you don't require context about the user/recipient/subject - for instance, when displaying the same data to all authenticated users:

```python
from fastapi import FastAPI, Depends
from authx import AuthX

app = FastAPI()
security = AuthX()

@app.get('/protected', dependencies=[Depends(security.access_token_required)])
def protected():
    ...
```

Here, the AuthX dependency is used at the route level solely for authentication enforcement.

If recipient context is necessary in the route logic, you can pass the dependency to the function to retrieve a `TokenPayload` or a custom ORM object:

```python
from fastapi import FastAPI, Depends
from authx import AuthX, TokenPayload

app = FastAPI()
security = AuthX()

@app.get('/protected')
def protected(payload: TokenPayload = Depends(security.access_token_required)):
    ...
```

In this scenario, the dependency is used as a function dependency, making the return value available as a function argument.

## Application-wide Application

Applying dependencies at the application level can be useful if your application is only responsible for protecting routes, not providing authentication tokens:

```python
from fastapi import FastAPI, Depends
from authx import AuthX, TokenPayload

app = FastAPI(dependencies=[Depends(security.access_token_required)])

security = AuthX()

@app.get('/protected')
def protected(payload: TokenPayload = Depends(security.access_token_required)):
    ...

@app.get('/protected/nocontext')
def protected_no_context():
    ...
```

Here, dependencies defined at the application level are applied to all routes. If context data is required in the route logic, you must still apply the dependency.

All routes in the example above require a valid access token. Note that to access context in route logic, the required dependency must be specified.

## API Router (FastAPI)

For scenarios where global dependencies are too restrictive, `fastapi.APIRouter` can be used to apply AuthX dependencies to a subset of routes.

=== "app.py"

    ```python title="app.py"
    from fastapi import FastAPI
    from authx import AuthX

    app = FastAPI()
    security = AuthX()

    @app.get('/')
    def home():
        return "Hello, World!"
    ```
=== "router.py"

    ```python title="router.py"
    from fastapi import APIRouter, Depends

    from app import security

    router = APIRouter(dependencies=[Depends(security.access_token_required)])

    @router.get('/protected'):
    def protected():
        return "This is a protected endpoint"
    ```

    Here, the dependency is included in the APIRouter definition.

=== "main.py"

    ```python title="main.py"
    from app import app
    from app import security
    from router import router

    app.include_router(
        router,
        dependencies=[Depends(security.access_token_required)]
    )
    ```

    You can include the dependency when including the router within the application. This syntax takes precedence over the one in `router.py`.

!!! note "Note on Performance"
    In routes where context is needed, the dependency seems to be called twice. However, FastAPI handles runtime execution efficiently and does not execute the dependency multiple times.
