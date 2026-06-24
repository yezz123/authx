"""AuthManager for multiple isolated AuthX contexts."""

from collections.abc import Awaitable, Callable, Mapping, Sequence
from typing import Any, Optional

from fastapi import Depends, Request
from fastapi.security import HTTPBearer

from authx._internal._error import _ErrorHandler
from authx.exceptions import (
    BadConfigurationError,
    JWTDecodeError,
    LoginTypeMismatchError,
    PolicyDeniedError,
    RevokedTokenError,
)
from authx.main import _OPENAPI_BEARER_DESCRIPTION, AuthX, _noop_openapi_security
from authx.policy import (
    PolicyContext,
    PolicyEngine,
    PolicyEvaluator,
    PolicyRule,
    build_policy_environment,
    default_subject_from_payload,
)
from authx.schema import RequestToken, TokenPayload, TokenResponse
from authx.types import DateTimeExpression, StringOrSequence, TokenLocations


class AuthManager(_ErrorHandler):
    """Manage multiple isolated AuthX instances by login type."""

    def __init__(
        self,
        policy_engine: Optional[PolicyEngine] = None,
        policy_rules: Optional[Sequence[PolicyRule]] = None,
    ) -> None:
        """Initialize AuthManager.

        Args:
            policy_engine: Optional policy engine instance.
            policy_rules: Optional rules used when creating the default policy engine.
        """
        self._auth_by_type: dict[str, AuthX[Any]] = {}
        self.policy_engine = policy_engine or PolicyEngine(rules=policy_rules)

    @property
    def login_types(self) -> tuple[str, ...]:
        """Return registered login types."""
        return tuple(self._auth_by_type)

    def register(self, auth: AuthX[Any]) -> None:
        """Register an AuthX instance with a unique login type."""
        if auth.login_type is None:
            raise BadConfigurationError("AuthX instances registered with AuthManager require a login_type")
        if auth.login_type in self._auth_by_type:
            raise BadConfigurationError(f"AuthX login_type '{auth.login_type}' is already registered")
        self._auth_by_type[auth.login_type] = auth

    def get(self, login_type: str) -> AuthX[Any]:
        """Return the AuthX instance for a login type."""
        try:
            return self._auth_by_type[login_type]
        except KeyError as e:
            raise BadConfigurationError(f"Unknown login_type '{login_type}'") from e

    def add_policy_rule(self, rule: PolicyRule) -> None:
        """Register a policy rule."""
        self.policy_engine.add_rule(rule)

    def add_policy_evaluator(self, evaluator: PolicyEvaluator) -> None:
        """Register a global policy evaluator."""
        self.policy_engine.add_evaluator(evaluator)

    def create_access_token(
        self,
        login_type: str,
        uid: str,
        fresh: bool = False,
        headers: Optional[dict[str, Any]] = None,
        expiry: Optional[DateTimeExpression] = None,
        data: Optional[dict[str, Any]] = None,
        audience: Optional[StringOrSequence] = None,
        scopes: Optional[list[str]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """Create an access token for a registered login type."""
        auth = self.get(login_type)
        return auth.create_access_token(uid, fresh, headers, expiry, data, audience, scopes, *args, **kwargs)

    def create_refresh_token(
        self,
        login_type: str,
        uid: str,
        headers: Optional[dict[str, Any]] = None,
        expiry: Optional[DateTimeExpression] = None,
        data: Optional[dict[str, Any]] = None,
        audience: Optional[StringOrSequence] = None,
        scopes: Optional[list[str]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """Create a refresh token for a registered login type."""
        auth = self.get(login_type)
        return auth.create_refresh_token(uid, headers, expiry, data, audience, scopes, *args, **kwargs)

    def create_token_pair(
        self,
        login_type: str,
        uid: str,
        fresh: bool = False,
        headers: Optional[dict[str, Any]] = None,
        access_expiry: Optional[DateTimeExpression] = None,
        refresh_expiry: Optional[DateTimeExpression] = None,
        data: Optional[dict[str, Any]] = None,
        audience: Optional[StringOrSequence] = None,
        access_scopes: Optional[list[str]] = None,
        refresh_scopes: Optional[list[str]] = None,
    ) -> TokenResponse:
        """Create access and refresh tokens for a registered login type."""
        return self.get(login_type).create_token_pair(
            uid=uid,
            fresh=fresh,
            headers=headers,
            access_expiry=access_expiry,
            refresh_expiry=refresh_expiry,
            data=data,
            audience=audience,
            access_scopes=access_scopes,
            refresh_scopes=refresh_scopes,
        )

    def token_required(
        self,
        login_type: str,
        type: str = "access",
        verify_type: bool = True,
        verify_fresh: bool = False,
        verify_csrf: Optional[bool] = None,
        locations: Optional[TokenLocations] = None,
    ) -> Callable[[Request], Awaitable[TokenPayload]]:
        """Dependency factory requiring a token for a specific login type."""
        header_scheme, cookie_scheme, query_scheme = self._openapi_security_dependencies(
            login_type=login_type,
            type=type,
            locations=locations,
        )
        header_dependency = Depends(header_scheme)
        cookie_dependency = Depends(cookie_scheme)
        query_dependency = Depends(query_scheme)

        async def _auth_required(
            request: Request,
            _authx_openapi_header: Any = header_dependency,
            _authx_openapi_cookie: Any = cookie_dependency,
            _authx_openapi_query: Any = query_dependency,
        ) -> TokenPayload:
            self.ensure_request_exception_handlers(request)
            return await self._auth_required(
                login_type=login_type,
                request=request,
                type=type,
                verify_type=verify_type,
                verify_fresh=verify_fresh,
                verify_csrf=verify_csrf,
                locations=locations,
            )

        return _auth_required

    def _openapi_security_dependencies(
        self,
        login_type: str,
        type: str = "access",
        locations: Optional[TokenLocations] = None,
    ) -> tuple[Callable[..., Any], Callable[..., Any], Callable[..., Any]]:
        try:
            return self.get(login_type)._openapi_security_dependencies(type=type, locations=locations)
        except BadConfigurationError:
            return (
                HTTPBearer(
                    scheme_name="AuthXBearer",
                    bearerFormat="JWT",
                    description=_OPENAPI_BEARER_DESCRIPTION,
                    auto_error=False,
                ),
                _noop_openapi_security,
                _noop_openapi_security,
            )

    def access_token_required(self, login_type: str) -> Callable[[Request], Awaitable[TokenPayload]]:
        """Dependency factory requiring an access token for a login type."""
        return self.token_required(login_type=login_type, type="access")

    def refresh_token_required(self, login_type: str) -> Callable[[Request], Awaitable[TokenPayload]]:
        """Dependency factory requiring a refresh token for a login type."""
        return self.token_required(login_type=login_type, type="refresh")

    def fresh_token_required(self, login_type: str) -> Callable[[Request], Awaitable[TokenPayload]]:
        """Dependency factory requiring a fresh access token for a login type."""
        return self.token_required(login_type=login_type, type="access", verify_fresh=True)

    async def _auth_required(
        self,
        login_type: str,
        request: Request,
        type: str = "access",
        verify_type: bool = True,
        verify_fresh: bool = False,
        verify_csrf: Optional[bool] = None,
        locations: Optional[TokenLocations] = None,
    ) -> TokenPayload:
        auth = self.get(login_type)
        try:
            payload = await auth._auth_required(
                request=request,
                type=type,
                verify_type=verify_type,
                verify_fresh=verify_fresh,
                verify_csrf=verify_csrf,
                locations=locations,
            )
        except JWTDecodeError:
            mismatch = await self._decode_mismatched_login_type(
                expected_login_type=login_type,
                request=request,
                type=type,
                locations=locations,
            )
            if mismatch is not None:
                raise LoginTypeMismatchError(
                    expected_type=login_type, actual_type=mismatch, login_type=login_type
                ) from None
            raise

        self._verify_login_type(payload, login_type)
        return payload

    async def _decode_mismatched_login_type(
        self,
        expected_login_type: str,
        request: Request,
        type: str,
        locations: Optional[TokenLocations],
    ) -> Optional[str]:
        expected_auth = self.get(expected_login_type)
        request_token = await expected_auth.get_token_from_request(
            request=request,
            type="refresh" if type == "refresh" else "access",
            optional=False,
            locations=locations,
        )
        for registered_type, auth in self._auth_by_type.items():
            if registered_type == expected_login_type:
                continue
            payload = self._try_verify_with_auth(auth, request_token)
            if payload is not None:
                return self._payload_login_type(payload)
        return None

    def _try_verify_with_auth(self, auth: AuthX[Any], request_token: RequestToken) -> Optional[TokenPayload]:
        try:
            return auth.verify_token(request_token, verify_csrf=False)
        except (JWTDecodeError, RevokedTokenError):
            return None

    def _verify_login_type(self, payload: TokenPayload, expected_login_type: str) -> None:
        actual_login_type = self._payload_login_type(payload)
        if actual_login_type != expected_login_type:
            raise LoginTypeMismatchError(
                expected_type=expected_login_type,
                actual_type=actual_login_type,
                login_type=expected_login_type,
            )

    def _payload_login_type(self, payload: TokenPayload) -> Optional[str]:
        login_type = payload.login_type
        return str(login_type) if login_type is not None else None

    async def authorize(
        self,
        login_type: str,
        action: str,
        resource: str,
        *,
        payload: Optional[TokenPayload] = None,
        request: Optional[Request] = None,
        subject: Any = None,
        resource_attrs: Any = None,
        env: Optional[Mapping[str, Any]] = None,
    ) -> TokenPayload:
        """Authorize a token payload against the policy engine."""
        if payload is None:
            if request is None:
                raise PolicyDeniedError(
                    "A request or token payload is required for policy authorization",
                    login_type=login_type,
                )
            payload = await self._auth_required(login_type=login_type, request=request)
        else:
            self._verify_login_type(payload, login_type)

        context = PolicyContext(
            login_type=login_type,
            action=action,
            resource=resource,
            payload=payload,
            request=request,
            subject=subject if subject is not None else default_subject_from_payload(payload),
            resource_attrs=resource_attrs or {},
            environment=build_policy_environment(request=request, environment=env),
        )
        decision = await self.policy_engine.evaluate(context)
        if not decision.allowed:
            raise PolicyDeniedError(decision.reason, login_type=login_type)
        return payload

    def policy_required(
        self,
        login_type: str,
        action: str,
        resource: str,
        *,
        subject: Any = None,
        resource_attrs: Any = None,
        env: Optional[Mapping[str, Any]] = None,
    ) -> Callable[[Request], Awaitable[TokenPayload]]:
        """Dependency factory requiring policy authorization."""
        header_scheme, cookie_scheme, query_scheme = self._openapi_security_dependencies(login_type=login_type)
        header_dependency = Depends(header_scheme)
        cookie_dependency = Depends(cookie_scheme)
        query_dependency = Depends(query_scheme)

        async def _policy_required(
            request: Request,
            _authx_openapi_header: Any = header_dependency,
            _authx_openapi_cookie: Any = cookie_dependency,
            _authx_openapi_query: Any = query_dependency,
        ) -> TokenPayload:
            self.ensure_request_exception_handlers(request)
            return await self.authorize(
                login_type=login_type,
                action=action,
                resource=resource,
                request=request,
                subject=subject,
                resource_attrs=resource_attrs,
                env=env,
            )

        return _policy_required
