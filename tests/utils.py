from typing import NamedTuple, Optional

from fastapi import Depends, FastAPI

from authx import AuthX, AuthXConfig, AuthXDependency, RequestToken, TokenPayload


class SecuritiesTuple(NamedTuple):
    """Named Tuple for AuthX dependencies."""

    access_token_headers: TokenPayload
    access_token_json: TokenPayload
    access_token_query: TokenPayload
    access_token_cookies: TokenPayload
    refresh_token_headers: TokenPayload
    refresh_token_json: TokenPayload
    refresh_token_query: TokenPayload
    refresh_token_cookies: TokenPayload


def init_app(config: Optional[AuthXConfig] = None) -> 'tuple[FastAPI, AuthX]':
    """Initialize FastAPI app and AuthX instance."""

    app = FastAPI()
    security = AuthX(config=(config or AuthXConfig()))

    return app, security


def create_securities(security: AuthX) -> SecuritiesTuple:
    """Create a named tuple with all AuthX dependencies."""

    return SecuritiesTuple(
        access_token_headers=Depends(
            security.token_required(
                locations=["headers"],
            )
        ),
        access_token_json=Depends(
            security.token_required(
                locations=["json"],
            )
        ),
        access_token_query=Depends(
            security.token_required(
                locations=["query"],
            )
        ),
        access_token_cookies=Depends(
            security.token_required(
                locations=["cookies"],
            )
        ),
        refresh_token_headers=Depends(
            security.token_required(
                locations=["headers"],
                type="refresh",
            )
        ),
        refresh_token_json=Depends(
            security.token_required(
                locations=["json"],
                type="refresh",
            )
        ),
        refresh_token_query=Depends(
            security.token_required(
                locations=["query"],
                type="refresh",
            )
        ),
        refresh_token_cookies=Depends(
            security.token_required(
                locations=["cookies"],
                type="refresh",
            )
        ),
    )


def create_get_token_routes(app: FastAPI, security: AuthX) -> None:
    """Create routes to get tokens from request."""

    @app.post("/read/access")
    def _access_token_route(
        token: RequestToken = Depends(security.get_token_from_request()),
    ):
        return token

    @app.post("/read/refresh")
    def _refresh_token_route(
        token: RequestToken = Depends(security.get_token_from_request(type="refresh")),
    ):
        return token


def create_token_routes(app: FastAPI, security: AuthX) -> None:
    """Create routes to get tokens from AuthX instance."""

    @app.get("/token/access")
    def _access_token_route(deps: AuthXDependency = security.DEPENDENCY):
        token = deps.create_access_token(uid="test", fresh=False)
        deps.set_access_cookies(token)
        return {"token": token}

    @app.get("/token/fresh")
    def _fresh_token_route(deps: AuthXDependency = security.DEPENDENCY):
        token = deps.create_access_token(uid="test", fresh=True)
        deps.set_access_cookies(token)
        return {"token": token}

    @app.get("/token/refresh")
    def _refresh_token_route(deps: AuthXDependency = security.DEPENDENCY):
        token = deps.create_refresh_token(uid="test")
        deps.set_refresh_cookies(token)
        return {"token": token}


def create_secure_routes(app: FastAPI, securities: SecuritiesTuple) -> None:
    """Create routes to test AuthX dependencies."""

    @app.get("/access_token/headers", dependencies=[securities.access_token_headers])
    async def _access_token_headers_route():
        return {"message": "Access Token Headers"}

    @app.post("/access_token/json", dependencies=[securities.access_token_json])
    async def _access_token_json_route():
        return {"message": "Access Token JSON"}

    @app.get("/access_token/query", dependencies=[securities.access_token_query])
    async def _access_token_query_route():
        return {"message": ""}

    @app.get("/access_token/cookies", dependencies=[securities.access_token_cookies])
    async def _access_token_cookies_route():
        return {"message": "Access Token"}

    @app.get("/refresh_token/headers", dependencies=[securities.refresh_token_headers])
    async def _refresh_token_headers_route():
        return {"message": "Refresh Token Headers"}

    @app.post("/refresh_token/json", dependencies=[securities.refresh_token_json])
    async def _refresh_token_json_route():
        return {"message": "Refresh Token JSON"}

    @app.get("/refresh_token/query", dependencies=[securities.refresh_token_query])
    async def _refresh_token_query_route():
        return {"message": "Refresh Token Query"}

    @app.get("/refresh_token/cookies", dependencies=[securities.refresh_token_cookies])
    async def _refresh_token_cookies_route():
        return {"message": "Refresh Token Cookies"}


def create_protected_routes(app: FastAPI, security: AuthX) -> None:
    """Create routes to test AuthX dependencies."""

    @app.post("/protected/access", dependencies=[security.ACCESS_REQUIRED])
    async def _protected_access_post():
        return {"message": "Protected Route"}

    @app.post("/protected/refresh", dependencies=[security.REFRESH_REQUIRED])
    async def _protected_refresh_route():
        return {"message": "Protected Refresh Route"}

    @app.post("/protected/fresh", dependencies=[security.FRESH_REQUIRED])
    async def _protected_fresh_route():
        return {"message": "Protected Fresh Route"}


def create_blocklist_routes(app: FastAPI, security: AuthX) -> None:
    """Create routes to test AuthX dependencies."""

    BLOCKLIST = set()

    @security.set_callback_token_blocklist
    def _is_in_blocklist(token: str) -> bool:
        return token in BLOCKLIST

    @app.get("/blocklist")
    async def _get_blocklist():
        return {"blocklist": list(BLOCKLIST)}

    @app.post("/token/block")
    async def _blocklist_access_route(
        access: Optional[RequestToken] = security.ACCESS_TOKEN,
        refresh: Optional[RequestToken] = security.REFRESH_TOKEN,
    ):
        if access:
            BLOCKLIST.add(access.token)
        if refresh:
            BLOCKLIST.add(refresh.token)
        return {"access": access, "refresh": refresh}


def create_subject_routes(app: FastAPI, security: AuthX) -> None:
    """Create routes to test AuthX dependencies."""

    USER_DB = {
        "test": {"uid": "test", "email": "test@test.com"},
        "foo": {"uid": "foo", "email": "foo@bar.com"},
    }
    RESOURCES = []

    @security.set_subject_getter
    def _get_subject(uid: str) -> dict:
        return USER_DB.get(uid)

    @app.get("/entity/resources")
    async def _resources_get():
        return {"resources": RESOURCES}

    @app.post("/entity/resources")
    async def _resource_post(
        data: dict,
    ):
        if "subject" in data:
            RESOURCES.append(data)
            return {"resource": data}
        return {"message": "Subject not found", "data": data}

    @app.get("/entitiy/subjects", dependencies=[security.CURRENT_SUBJECT])
    async def _subjects_route():
        return {"subjects": list(USER_DB.values())}

    @app.get("/entitiy/subject")
    async def _subject_route(subject: dict = security.CURRENT_SUBJECT):
        return {"subject": subject}

    @app.get("/entity/subject/resources")
    async def _subject_resources_route(subject: dict = security.CURRENT_SUBJECT):
        return {"resources": [r for r in RESOURCES if subject["uid"] == r["subject"]]}
