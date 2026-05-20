"""Policy engine primitives for AuthX authorization."""

import inspect
from collections.abc import Awaitable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal, Optional, Protocol, Union

from fastapi import Request

from authx._internal._scopes import has_required_scopes, match_scope
from authx.exceptions import PolicyEvaluationError
from authx.schema import TokenPayload

PolicyEffect = Literal["allow", "deny"]
PolicySource = Literal["subject", "resource", "environment", "token"]
PolicyOperator = Literal[
    "equals",
    "not_equals",
    "in",
    "not_in",
    "contains",
    "gt",
    "gte",
    "lt",
    "lte",
    "exists",
]


def _read_value(source: Any, key: str) -> Any:
    """Read a dotted value from mappings or objects."""
    current = source
    for part in key.split("."):
        if current is None:
            return None
        if isinstance(current, Mapping):
            current = current.get(part)
        else:
            current = getattr(current, part, None)
    return current


def _as_sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, Sequence):
        return value
    return [value]


@dataclass(frozen=True)
class PolicyCondition:
    """A condition evaluated against a policy context source."""

    source: PolicySource
    key: str
    operator: PolicyOperator = "equals"
    value: Any = None

    def matches(self, context: "PolicyContext") -> bool:
        """Return whether this condition matches the given context."""
        candidate = _read_value(context.get_source(self.source), self.key)

        if self.operator == "exists":
            return candidate is not None
        if self.operator == "equals":
            return candidate == self.value
        if self.operator == "not_equals":
            return candidate != self.value
        if self.operator == "in":
            return candidate in _as_sequence(self.value)
        if self.operator == "not_in":
            return candidate not in _as_sequence(self.value)
        if self.operator == "contains":
            if candidate is None:
                return False
            return self.value in candidate
        if self.operator == "gt":
            return candidate is not None and candidate > self.value
        if self.operator == "gte":
            return candidate is not None and candidate >= self.value
        if self.operator == "lt":
            return candidate is not None and candidate < self.value
        if self.operator == "lte":
            return candidate is not None and candidate <= self.value
        raise PolicyEvaluationError(f"Unsupported policy operator: {self.operator}")  # pragma: no cover


class PolicyEvaluator(Protocol):
    """Protocol for custom policy evaluators."""

    def __call__(self, context: "PolicyContext", rule: "PolicyRule") -> Union[bool, Awaitable[bool]]:
        """Evaluate a policy context and rule."""
        ...


@dataclass(frozen=True)
class PolicyContext:
    """Context passed to policy evaluators."""

    login_type: str
    action: str
    resource: str
    payload: Optional[TokenPayload] = None
    request: Optional[Request] = None
    subject: Any = None
    resource_attrs: Any = None
    environment: Mapping[str, Any] = field(default_factory=dict)

    def get_source(self, source: PolicySource) -> Any:
        """Return a named source for policy conditions."""
        if source == "subject":
            return self.subject
        if source == "resource":
            return self.resource_attrs
        if source == "environment":
            return self.environment
        if source == "token" and self.payload is not None:
            return self.payload.model_dump()
        if source == "token":
            return {}
        raise PolicyEvaluationError(f"Unsupported policy source: {source}")  # pragma: no cover


@dataclass(frozen=True)
class PolicyRule:
    """A single authorization rule."""

    effect: PolicyEffect
    actions: Sequence[str]
    resources: Sequence[str]
    conditions: Sequence[PolicyCondition] = field(default_factory=list)
    scopes: Optional[Sequence[str]] = None
    all_scopes_required: bool = True
    evaluators: Sequence[PolicyEvaluator] = field(default_factory=list)
    reason: Optional[str] = None

    def matches_action(self, action: str) -> bool:
        """Return whether the requested action matches this rule."""
        return any(rule_action == "*" or match_scope(action, rule_action) for rule_action in self.actions)

    def matches_resource(self, resource: str) -> bool:
        """Return whether the requested resource matches this rule."""
        return any(rule_resource == "*" or match_scope(resource, rule_resource) for rule_resource in self.resources)

    def matches_scopes(self, payload: Optional[TokenPayload]) -> bool:
        """Return whether token scopes satisfy this rule."""
        if self.scopes is None:
            return True
        provided = payload.scopes if payload is not None else None
        return has_required_scopes(self.scopes, provided, all_required=self.all_scopes_required)


@dataclass(frozen=True)
class PolicyDecision:
    """Result of policy evaluation."""

    allowed: bool
    reason: str
    rule: Optional[PolicyRule] = None


class PolicyEngine:
    """Evaluate policy rules for AuthX-managed identities."""

    def __init__(
        self,
        rules: Optional[Sequence[PolicyRule]] = None,
        evaluators: Optional[Sequence[PolicyEvaluator]] = None,
        default_allow: bool = False,
    ) -> None:
        """Initialize the policy engine.

        Args:
            rules: Initial policy rules.
            evaluators: Global custom evaluators that must pass for matching rules.
            default_allow: Whether to allow requests when no rule matches.
        """
        self._rules = list(rules or [])
        self._evaluators = list(evaluators or [])
        self.default_allow = default_allow

    @property
    def rules(self) -> list[PolicyRule]:
        """Return registered policy rules."""
        return list(self._rules)

    def add_rule(self, rule: PolicyRule) -> None:
        """Register a policy rule."""
        self._rules.append(rule)

    def add_evaluator(self, evaluator: PolicyEvaluator) -> None:
        """Register a global custom policy evaluator."""
        self._evaluators.append(evaluator)

    async def evaluate(self, context: PolicyContext) -> PolicyDecision:
        """Evaluate context against registered rules.

        Explicit deny rules win over allow rules. If no rule matches, the
        configured default decision is returned.
        """
        allow_decision: Optional[PolicyDecision] = None
        for rule in self._rules:
            if not await self._matches_rule(context, rule):
                continue

            reason = rule.reason or f"Policy rule {rule.effect} matched"
            decision = PolicyDecision(allowed=(rule.effect == "allow"), reason=reason, rule=rule)
            if rule.effect == "deny":
                return decision
            allow_decision = decision

        if allow_decision is not None:
            return allow_decision

        if self.default_allow:
            return PolicyDecision(allowed=True, reason="No policy rule matched; default allow")
        return PolicyDecision(allowed=False, reason="No policy rule matched")

    async def _matches_rule(self, context: PolicyContext, rule: PolicyRule) -> bool:
        if not rule.matches_action(context.action):
            return False
        if not rule.matches_resource(context.resource):
            return False
        if not rule.matches_scopes(context.payload):
            return False
        if not all(condition.matches(context) for condition in rule.conditions):
            return False
        return await self._run_evaluators(context, rule)

    async def _run_evaluators(self, context: PolicyContext, rule: PolicyRule) -> bool:
        for evaluator in [*self._evaluators, *rule.evaluators]:
            result = evaluator(context, rule)
            if inspect.isawaitable(result):
                result = await result
            if not result:
                return False
        return True


def build_policy_environment(
    request: Optional[Request] = None,
    environment: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """Build an environment mapping for policy evaluation."""
    now = datetime.now(timezone.utc)
    values: dict[str, Any] = {
        "time": now,
        "hour": now.hour,
        "weekday": now.weekday(),
    }
    if request is not None:
        values["method"] = request.method
        values["path"] = request.url.path
        values["client_ip"] = request.client.host if request.client is not None else None
    if environment is not None:
        values.update(environment)
    return values


def default_subject_from_payload(payload: Optional[TokenPayload]) -> dict[str, Any]:
    """Build a default subject mapping from token payload claims."""
    if payload is None:
        return {}
    subject = payload.extra_dict.copy()
    subject["sub"] = payload.sub
    subject["scopes"] = payload.scopes or []
    subject["login_type"] = payload.login_type
    return subject
