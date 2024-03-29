# Dependency Bundle

To streamline code and maintain logical coherence, AuthX offers a method for injecting a dependency bundle into route functions via `AuthX.get_dependency`.

`AuthX.get_dependency` returns an `AuthXDependency` instance associated with the request and response of the route. This object encompasses all dependencies available in `AuthX`.

Illustrating the effectiveness of `AuthXDependency` in reducing code complexity, let's focus on authentication via Cookies.

=== "With Bundle"
    ```python hl_lines="16 22"
    from pydantic import BaseModel
    from fastapi import FastAPI, Depends
    from authx import AuthX, AuthXDependency

    app = FastAPI()
    security = AuthX()

    class LoginData:
        username: str
        password: str

    @app.post('/login')
    def login(data: LoginData, deps: AuthXDependency = Depends(security.get_dependency)):
        if data.username == "test" and data.password == "test":
            token = deps.create_access_token(uid="test")
            deps.set_access_cookie(token)
            return "CONNECTED"
        return "NOT CONNECTED"

    @app.post('/logout', dependencies=[Depends(security.access_token_required)])
    def logout(deps: AuthXDependency = Depends(security.get_dependency)):
        deps.unset_access_cookies()
        return "DISCONNECTED"
    ```
=== "Without Bundle"
    ```python linenums="1" hl_lines="17 18 24 25"
    from pydantic import BaseModel
    from fastapi import FastAPI, Depends
    from fastapi.responses import JSONResponse
    from authx import AuthX

    app = FastAPI()
    security = AuthX()

    class LoginData:
        username: str
        password: str

    @app.post('/login')
    def login(data: LoginData):
        if data.username == "test" and data.password == "test":
            token = security.create_access_token(uid="test")
            response = JSONResponse(status_code=200, content="CONNECTED")
            security.set_access_cookie(token, response)
            return response
        return "NOT CONNECTED"

    @app.post('/logout', dependencies=[Depends(security.access_token_required)])
    def logout():
        response = JSONResponse(status_code=200, content="DISCONNECTED")
        security.unset_access_cookies(response)
        return response
    ```

The primary distinction between these two code snippets lies in the implicit context provided by `AuthXDependency`. There's no need to access the request or create a response object explicitly to set/unset cookies, for instance. This not only reduces code but also ensures that you stay within the bounds of your function logic.

While this example is straightforward, it becomes highly beneficial when dealing with numerous dependencies within your route functions. It enables you to maintain clean and focused code, centered on your application's logic.
