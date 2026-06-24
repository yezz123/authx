from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from authx import AuthManager, AuthX, AuthXConfig, TokenPayload

OPENAPI_BEARER_DESCRIPTION = (
    "Paste an AuthX JWT from create_access_token/create_refresh_token, not JWT_SECRET_KEY. "
    "The Bearer prefix is optional in Swagger UI."
)


def test_access_token_required_adds_openapi_bearer_security_metadata():
    auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="secret"))
    app = FastAPI()

    @app.get("/protected")
    async def protected(payload: Annotated[TokenPayload, Depends(auth.access_token_required)]):
        return {"sub": payload.sub}

    openapi = app.openapi()

    assert openapi["components"]["securitySchemes"] == {
        "AuthXBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": OPENAPI_BEARER_DESCRIPTION,
        }
    }
    assert openapi["paths"]["/protected"]["get"]["security"] == [{"AuthXBearer": []}]


def test_route_level_access_token_required_adds_openapi_security_metadata():
    auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="secret"))
    app = FastAPI()

    @app.get("/protected", dependencies=[Depends(auth.access_token_required)])
    async def protected():
        return {"ok": True}

    openapi = app.openapi()

    assert openapi["components"]["securitySchemes"]["AuthXBearer"]["scheme"] == "bearer"
    assert openapi["paths"]["/protected"]["get"]["security"] == [{"AuthXBearer": []}]


def test_token_locations_add_matching_openapi_security_schemes():
    auth = AuthX(
        config=AuthXConfig(
            JWT_SECRET_KEY="secret",
            JWT_TOKEN_LOCATION=["headers", "cookies", "query", "json"],
        )
    )
    app = FastAPI()

    @app.get("/protected", dependencies=[Depends(auth.access_token_required)])
    async def protected():
        return {"ok": True}

    openapi = app.openapi()

    assert openapi["components"]["securitySchemes"] == {
        "AuthXBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": OPENAPI_BEARER_DESCRIPTION,
        },
        "AuthXAccessCookie": {
            "type": "apiKey",
            "in": "cookie",
            "name": "access_token_cookie",
            "description": "Provide an AuthX access token in this cookie.",
        },
        "AuthXQuery": {
            "type": "apiKey",
            "in": "query",
            "name": "token",
            "description": "Provide an AuthX JWT in this query parameter.",
        },
    }
    assert openapi["paths"]["/protected"]["get"]["security"] == [
        {"AuthXBearer": []},
        {"AuthXAccessCookie": []},
        {"AuthXQuery": []},
    ]


def test_openapi_security_dependency_does_not_require_authorization_header_for_cookie_tokens():
    config = AuthXConfig(
        JWT_SECRET_KEY="secret",
        JWT_TOKEN_LOCATION=["cookies"],
        JWT_COOKIE_CSRF_PROTECT=False,
    )
    auth = AuthX(config=config)
    app = FastAPI()

    @app.get("/protected")
    async def protected(payload: Annotated[TokenPayload, Depends(auth.access_token_required)]):
        return {"sub": payload.sub}

    token = auth.create_access_token(uid="alice")
    response = TestClient(app).get("/protected", cookies={config.JWT_ACCESS_COOKIE_NAME: token})

    assert response.status_code == 200
    assert response.json() == {"sub": "alice"}


def test_access_token_required_accepts_valid_swagger_bearer_token():
    auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="secret"))
    app = FastAPI()

    @app.get("/protected")
    async def protected(payload: Annotated[TokenPayload, Depends(auth.access_token_required)]):
        return {"sub": payload.sub}

    token = auth.create_access_token(uid="alice")
    response = TestClient(app).get("/protected", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {"sub": "alice"}


def test_access_token_required_handles_invalid_token_without_registered_error_handlers():
    auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="secret"))
    app = FastAPI()

    @app.get("/protected")
    async def protected(payload: Annotated[TokenPayload, Depends(auth.access_token_required)]):
        return {"sub": payload.sub}

    response = TestClient(app).get("/protected", headers={"Authorization": "Bearer secret"})

    assert response.status_code == 422
    assert response.json() == {
        "message": "Invalid Token",
        "error_type": "JWTDecodeError",
    }


def test_access_token_required_handles_missing_token_without_registered_error_handlers():
    auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="secret"))
    app = FastAPI()

    @app.get("/protected")
    async def protected(payload: Annotated[TokenPayload, Depends(auth.access_token_required)]):
        return {"sub": payload.sub}

    response = TestClient(app).get("/protected")

    assert response.status_code == 401
    assert response.json() == {
        "message": "Token Error",
        "error_type": "MissingTokenError",
    }


def test_access_token_required_uses_registered_error_handlers_when_present():
    auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="secret"))
    auth.MSG_JWTDecodeError = "Custom invalid token"
    app = FastAPI()
    auth.handle_errors(app)

    @app.get("/protected")
    async def protected(payload: Annotated[TokenPayload, Depends(auth.access_token_required)]):
        return {"sub": payload.sub}

    response = TestClient(app).get("/protected", headers={"Authorization": "Bearer secret"})

    assert response.status_code == 422
    assert response.json() == {
        "message": "Custom invalid token",
        "error_type": "JWTDecodeError",
    }


def test_manager_access_token_required_adds_openapi_security_metadata():
    manager = AuthManager()
    manager.register(
        AuthX(
            config=AuthXConfig(
                JWT_SECRET_KEY="admin-secret",
                JWT_TOKEN_LOCATION=["headers"],
            ),
            login_type="admin",
        )
    )
    app = FastAPI()

    @app.get("/admin", dependencies=[Depends(manager.access_token_required("admin"))])
    async def admin():
        return {"ok": True}

    openapi = app.openapi()

    assert openapi["components"]["securitySchemes"]["AuthXBearer"]["scheme"] == "bearer"
    assert openapi["paths"]["/admin"]["get"]["security"] == [{"AuthXBearer": []}]
