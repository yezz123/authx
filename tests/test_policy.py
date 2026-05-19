"""Tests for policy engine authorization."""

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from authx import AuthManager, AuthX, AuthXConfig
from authx.policy import PolicyCondition, PolicyContext, PolicyEngine, PolicyRule


def make_manager_with_auth(*rules: PolicyRule) -> tuple[AuthManager, AuthX]:
    """Create a manager with a single admin AuthX instance."""
    manager = AuthManager(policy_rules=list(rules))
    auth = AuthX(
        config=AuthXConfig(
            JWT_SECRET_KEY="admin-secret",
            JWT_TOKEN_LOCATION=["headers"],
        ),
        login_type="admin",
    )
    manager.register(auth)
    return manager, auth


@pytest.mark.asyncio
async def test_policy_allows_matching_action_resource_and_scope():
    engine = PolicyEngine(
        rules=[
            PolicyRule(
                effect="allow",
                actions=["users:ban"],
                resources=["users"],
                scopes=["admin:users:ban"],
            )
        ]
    )
    manager, _ = make_manager_with_auth()
    token = manager.create_access_token("admin", uid="root", scopes=["admin:*"])
    payload = manager.get("admin")._decode_token(token)

    decision = await engine.evaluate(
        PolicyContext(
            login_type="admin",
            action="users:ban",
            resource="users",
            payload=payload,
        )
    )

    assert decision.allowed is True


@pytest.mark.asyncio
async def test_policy_deny_rule_wins_over_allow_rule():
    engine = PolicyEngine(
        rules=[
            PolicyRule(effect="allow", actions=["users:*"], resources=["users"]),
            PolicyRule(effect="deny", actions=["users:delete"], resources=["users"], reason="delete disabled"),
        ]
    )
    decision = await engine.evaluate(PolicyContext(login_type="admin", action="users:delete", resource="users"))

    assert decision.allowed is False
    assert decision.reason == "delete disabled"


@pytest.mark.asyncio
async def test_policy_subject_resource_and_environment_conditions():
    engine = PolicyEngine(
        rules=[
            PolicyRule(
                effect="allow",
                actions=["documents:read"],
                resources=["documents"],
                conditions=[
                    PolicyCondition(source="subject", key="tenant_id", value="tenant-a"),
                    PolicyCondition(source="resource", key="tenant_id", value="tenant-a"),
                    PolicyCondition(source="environment", key="method", value="GET"),
                ],
            )
        ]
    )
    context = PolicyContext(
        login_type="user",
        action="documents:read",
        resource="documents",
        subject={"tenant_id": "tenant-a"},
        resource_attrs={"tenant_id": "tenant-a"},
        environment={"method": "GET"},
    )

    decision = await engine.evaluate(context)

    assert decision.allowed is True


@pytest.mark.asyncio
async def test_policy_custom_callable_evaluator():
    def evaluator(context: PolicyContext, rule: PolicyRule) -> bool:
        return context.subject["account_status"] == "active"

    engine = PolicyEngine(
        rules=[
            PolicyRule(
                effect="allow",
                actions=["billing:read"],
                resources=["billing"],
                evaluators=[evaluator],
            )
        ]
    )

    allowed = await engine.evaluate(
        PolicyContext(
            login_type="user",
            action="billing:read",
            resource="billing",
            subject={"account_status": "active"},
        )
    )
    denied = await engine.evaluate(
        PolicyContext(
            login_type="user",
            action="billing:read",
            resource="billing",
            subject={"account_status": "suspended"},
        )
    )

    assert allowed.allowed is True
    assert denied.allowed is False


def test_policy_required_dependency_denies_without_matching_policy():
    manager, _ = make_manager_with_auth()
    app = FastAPI()
    manager.handle_errors(app)

    @app.get("/admin/users", dependencies=[Depends(manager.policy_required("admin", "users:ban", "users"))])
    def route():
        return {"ok": True}

    token = manager.create_access_token("admin", uid="root")
    response = TestClient(app).get("/admin/users", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
    assert response.json()["error_type"] == "PolicyDeniedError"


def test_policy_required_dependency_allows_matching_policy():
    manager, _ = make_manager_with_auth(
        PolicyRule(effect="allow", actions=["users:ban"], resources=["users"], scopes=["admin:*"])
    )
    app = FastAPI()
    manager.handle_errors(app)

    @app.get("/admin/users", dependencies=[Depends(manager.policy_required("admin", "users:ban", "users"))])
    def route():
        return {"ok": True}

    token = manager.create_access_token("admin", uid="root", scopes=["admin:*"])
    response = TestClient(app).get("/admin/users", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {"ok": True}
