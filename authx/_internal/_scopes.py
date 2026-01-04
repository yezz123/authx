"""Scope management utilities for AuthX.

This module provides functions for matching and validating scopes with support for:
- Simple string scopes (e.g., "read", "write", "admin")
- Hierarchical scopes with colon separator (e.g., "users:read", "posts:write")
- Wildcard patterns (e.g., "admin:*" matches "admin:users", "admin:settings")
"""

from collections.abc import Sequence


def match_scope(required: str, provided: str) -> bool:
    """Check if a provided scope matches a required scope.

    Supports wildcard matching where a scope ending with ":*" matches
    any scope under that namespace.

    Args:
        required: The scope that is required (e.g., "users:read").
        provided: The scope that was provided in the token (e.g., "users:*").

    Returns:
        True if the provided scope satisfies the required scope.

    Examples:
        >>> match_scope("read", "read")
        True
        >>> match_scope("users:read", "users:*")
        True
        >>> match_scope("users:read", "admin:*")
        False
        >>> match_scope("admin", "admin:*")
        True
        >>> match_scope("admin:users:edit", "admin:*")
        True
    """
    # Exact match
    if required == provided:
        return True

    # Wildcard match: "admin:*" should match "admin", "admin:users", "admin:users:edit"
    if provided.endswith(":*"):
        prefix = provided[:-1]  # Remove the "*" to get "admin:"
        namespace = provided[:-2]  # Remove ":*" to get "admin"
        # Match if required starts with "admin:" or equals "admin"
        return required.startswith(prefix) or required == namespace

    return False


def has_required_scopes(
    required: Sequence[str],
    provided: Sequence[str] | None,
    all_required: bool = True,
) -> bool:
    """Check if the provided scopes satisfy the required scopes.

    Args:
        required: List of scopes that are required.
        provided: List of scopes that were provided in the token.
        all_required: If True, all required scopes must be satisfied (AND logic).
                      If False, at least one required scope must be satisfied (OR logic).

    Returns:
        True if the scope requirements are satisfied.

    Examples:
        >>> has_required_scopes(["read"], ["read", "write"], all_required=True)
        True
        >>> has_required_scopes(["read", "admin"], ["read"], all_required=True)
        False
        >>> has_required_scopes(["read", "admin"], ["read"], all_required=False)
        True
        >>> has_required_scopes(["users:read"], ["users:*"], all_required=True)
        True
    """
    if provided is None:
        return len(required) == 0

    def scope_satisfied(req: str) -> bool:
        """Check if a single required scope is satisfied by any provided scope."""
        return any(match_scope(req, prov) for prov in provided)

    if all_required:
        # All required scopes must be satisfied
        return all(scope_satisfied(req) for req in required)
    else:
        # At least one required scope must be satisfied
        return any(scope_satisfied(req) for req in required)


def normalize_scope(scope: str) -> str:
    """Normalize a scope string by stripping whitespace and converting to lowercase.

    Args:
        scope: The scope string to normalize.

    Returns:
        The normalized scope string.
    """
    return scope.strip().lower()


def parse_scope_string(scope_string: str, delimiter: str = " ") -> list[str]:
    """Parse a space-separated scope string into a list of scopes.

    This is useful for OAuth2 compatibility where scopes are often passed
    as a single space-separated string.

    Args:
        scope_string: A string containing scopes separated by the delimiter.
        delimiter: The delimiter used to separate scopes. Defaults to space.

    Returns:
        A list of individual scope strings.

    Examples:
        >>> parse_scope_string("read write admin")
        ["read", "write", "admin"]
        >>> parse_scope_string("users:read users:write")
        ["users:read", "users:write"]
    """
    if not scope_string:
        return []
    return [s.strip() for s in scope_string.split(delimiter) if s.strip()]
