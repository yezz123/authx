"""Tests for policy engine authorization."""

from unittest.mock import Mock

import pytest
from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient

from authx import AuthManager, AuthX, AuthXConfig
from authx.exceptions import PolicyEvaluationError
from authx.policy import (
    PolicyCondition,
    PolicyContext,
    PolicyEngine,
    PolicyRule,
    build_policy_environment,
    default_subject_from_payload,
)
from authx.schema import TokenPayload


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


def test_policy_condition_operators_and_sources():
    payload = TokenPayload(sub="user1", login_type="admin", scopes=["admin:*"])
    subject = Mock()
    subject.profile = {"age": 30}
    context = PolicyContext(
        login_type="admin",
        action="users:read",
        resource="users",
        payload=payload,
        subject=subject,
        resource_attrs={"tags": ["internal", "active"], "owner": "user1"},
        environment={"hour": 10, "method": "GET"},
    )

    assert PolicyCondition("subject", "profile.age", "equals", 30).matches(context)
    assert PolicyCondition("resource", "owner", "not_equals", "user2").matches(context)
    assert PolicyCondition("environment", "method", "in", ["GET", "POST"]).matches(context)
    assert PolicyCondition("environment", "method", "not_in", ("DELETE", "PATCH")).matches(context)
    assert PolicyCondition("resource", "tags", "contains", "active").matches(context)
    assert PolicyCondition("resource", "missing", "contains", "active").matches(context) is False
    assert PolicyCondition("environment", "hour", "gt", 9).matches(context)
    assert PolicyCondition("environment", "hour", "gte", 10).matches(context)
    assert PolicyCondition("environment", "hour", "lt", 11).matches(context)
    assert PolicyCondition("environment", "hour", "lte", 10).matches(context)
    assert PolicyCondition("token", "login_type", "exists").matches(context)
    assert PolicyCondition("subject", "profile.missing", "exists").matches(context) is False


def test_policy_context_token_source_without_payload():
    context = PolicyContext(login_type="guest", action="read", resource="posts")

    assert context.get_source("token") == {}


def test_policy_condition_unsupported_source_raises():
    context = PolicyContext(login_type="guest", action="read", resource="posts")

    with pytest.raises(PolicyEvaluationError):
        context.get_source("unknown")  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_policy_engine_rule_mismatch_and_default_allow_branches():
    engine = PolicyEngine(
        rules=[
            PolicyRule(effect="allow", actions=["users:write"], resources=["users"]),
            PolicyRule(effect="allow", actions=["users:read"], resources=["posts"]),
            PolicyRule(
                effect="allow",
                actions=["users:read"],
                resources=["users"],
                scopes=["admin:*"],
            ),
            PolicyRule(
                effect="allow",
                actions=["users:read"],
                resources=["users"],
                conditions=[PolicyCondition("environment", "method", value="POST")],
            ),
        ],
        default_allow=True,
    )

    decision = await engine.evaluate(
        PolicyContext(
            login_type="admin",
            action="users:read",
            resource="users",
            environment={"method": "GET"},
        )
    )

    assert decision.allowed is True
    assert decision.reason == "No policy rule matched; default allow"


@pytest.mark.asyncio
async def test_policy_engine_add_rule_global_async_evaluator_and_rules_copy():
    async def evaluator(context: PolicyContext, rule: PolicyRule) -> bool:
        return context.environment["allowed"] is True

    engine = PolicyEngine()
    rule = PolicyRule(effect="allow", actions=["*"], resources=["*"])
    engine.add_rule(rule)
    engine.add_evaluator(evaluator)
    copied_rules = engine.rules
    copied_rules.clear()

    allowed = await engine.evaluate(
        PolicyContext(
            login_type="admin",
            action="anything",
            resource="anything",
            environment={"allowed": True},
        )
    )
    denied = await engine.evaluate(
        PolicyContext(
            login_type="admin",
            action="anything",
            resource="anything",
            environment={"allowed": False},
        )
    )

    assert engine.rules == [rule]
    assert allowed.allowed is True
    assert denied.allowed is False


def test_policy_rule_scopes_without_payload_and_or_logic():
    rule = PolicyRule(
        effect="allow",
        actions=["read"],
        resources=["documents"],
        scopes=["read", "admin"],
        all_scopes_required=False,
    )
    payload = TokenPayload(sub="user1", scopes=["read"])

    assert rule.matches_scopes(None) is False
    assert rule.matches_scopes(payload) is True


def test_build_policy_environment_with_request_and_overrides():
    request = Request(
        scope={
            "type": "http",
            "method": "POST",
            "path": "/admin/users",
            "headers": [],
            "client": ("127.0.0.1", 1234),
        }
    )

    environment = build_policy_environment(request=request, environment={"method": "OVERRIDE", "custom": "value"})

    assert environment["method"] == "OVERRIDE"
    assert environment["path"] == "/admin/users"
    assert environment["client_ip"] == "127.0.0.1"
    assert environment["custom"] == "value"


def test_default_subject_from_payload():
    payload = TokenPayload(sub="user1", scopes=["read"], login_type="user", role="editor")

    assert default_subject_from_payload(None) == {}
    assert default_subject_from_payload(payload) == {
        "sub": "user1",
        "scopes": ["read"],
        "login_type": "user",
    }
