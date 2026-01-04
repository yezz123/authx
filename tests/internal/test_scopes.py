"""Tests for scope management utilities."""

from authx._internal._scopes import (
    has_required_scopes,
    match_scope,
    normalize_scope,
    parse_scope_string,
)


class TestMatchScope:
    """Tests for match_scope function."""

    def test_exact_match(self):
        """Test exact scope matching."""
        assert match_scope("read", "read") is True
        assert match_scope("write", "write") is True
        assert match_scope("admin", "admin") is True

    def test_exact_mismatch(self):
        """Test exact scope non-matching."""
        assert match_scope("read", "write") is False
        assert match_scope("admin", "user") is False

    def test_hierarchical_exact_match(self):
        """Test hierarchical scope exact matching."""
        assert match_scope("users:read", "users:read") is True
        assert match_scope("posts:write", "posts:write") is True
        assert match_scope("admin:users:edit", "admin:users:edit") is True

    def test_hierarchical_mismatch(self):
        """Test hierarchical scope non-matching."""
        assert match_scope("users:read", "users:write") is False
        assert match_scope("posts:read", "users:read") is False

    def test_wildcard_match_simple(self):
        """Test wildcard matching with simple child scopes."""
        assert match_scope("admin:users", "admin:*") is True
        assert match_scope("admin:settings", "admin:*") is True
        assert match_scope("admin:logs", "admin:*") is True

    def test_wildcard_match_namespace(self):
        """Test wildcard matching the namespace itself."""
        assert match_scope("admin", "admin:*") is True

    def test_wildcard_match_nested(self):
        """Test wildcard matching nested scopes."""
        assert match_scope("admin:users:edit", "admin:*") is True
        assert match_scope("admin:users:delete", "admin:*") is True

    def test_wildcard_no_cross_namespace(self):
        """Test wildcard doesn't match different namespaces."""
        assert match_scope("users:read", "admin:*") is False
        assert match_scope("posts:write", "admin:*") is False

    def test_wildcard_partial_no_match(self):
        """Test that partial namespace doesn't match."""
        assert match_scope("administrator", "admin:*") is False

    def test_multiple_wildcards(self):
        """Test with multiple wildcard patterns."""
        assert match_scope("users:profile", "users:*") is True
        assert match_scope("posts:comments", "posts:*") is True


class TestHasRequiredScopes:
    """Tests for has_required_scopes function."""

    def test_single_scope_present(self):
        """Test single required scope present."""
        assert has_required_scopes(["read"], ["read", "write"]) is True

    def test_single_scope_missing(self):
        """Test single required scope missing."""
        assert has_required_scopes(["admin"], ["read", "write"]) is False

    def test_multiple_scopes_all_present(self):
        """Test multiple required scopes all present."""
        assert has_required_scopes(["read", "write"], ["read", "write", "delete"]) is True

    def test_multiple_scopes_some_missing(self):
        """Test multiple required scopes with some missing."""
        assert has_required_scopes(["read", "admin"], ["read", "write"]) is False

    def test_all_required_true(self):
        """Test AND logic (all_required=True)."""
        assert has_required_scopes(["read", "write"], ["read", "write"], all_required=True) is True
        assert has_required_scopes(["read", "admin"], ["read", "write"], all_required=True) is False

    def test_all_required_false(self):
        """Test OR logic (all_required=False)."""
        assert has_required_scopes(["read", "admin"], ["read", "write"], all_required=False) is True
        assert has_required_scopes(["admin", "superuser"], ["read", "write"], all_required=False) is False

    def test_wildcard_satisfaction(self):
        """Test wildcard scopes satisfy specific requirements."""
        assert has_required_scopes(["admin:users"], ["admin:*"]) is True
        assert has_required_scopes(["admin:settings"], ["admin:*"]) is True
        assert has_required_scopes(["admin:users", "admin:settings"], ["admin:*"]) is True

    def test_wildcard_multiple_namespaces(self):
        """Test wildcard with multiple namespace requirements."""
        assert has_required_scopes(["admin:users", "posts:read"], ["admin:*", "posts:*"]) is True
        assert has_required_scopes(["admin:users", "posts:read"], ["admin:*"]) is False

    def test_none_provided(self):
        """Test with None provided scopes."""
        assert has_required_scopes([], None) is True
        assert has_required_scopes(["read"], None) is False

    def test_empty_required(self):
        """Test with empty required scopes."""
        assert has_required_scopes([], ["read", "write"]) is True
        assert has_required_scopes([], []) is True

    def test_empty_provided(self):
        """Test with empty provided scopes."""
        assert has_required_scopes(["read"], []) is False
        assert has_required_scopes([], []) is True


class TestNormalizeScope:
    """Tests for normalize_scope function."""

    def test_strip_whitespace(self):
        """Test whitespace stripping."""
        assert normalize_scope("  read  ") == "read"
        assert normalize_scope("\twrite\n") == "write"

    def test_lowercase(self):
        """Test lowercase conversion."""
        assert normalize_scope("READ") == "read"
        assert normalize_scope("Admin:Users") == "admin:users"

    def test_combined(self):
        """Test combined normalization."""
        assert normalize_scope("  ADMIN:USERS  ") == "admin:users"


class TestParseScopeString:
    """Tests for parse_scope_string function."""

    def test_space_separated(self):
        """Test parsing space-separated scopes."""
        assert parse_scope_string("read write admin") == ["read", "write", "admin"]

    def test_single_scope(self):
        """Test parsing single scope."""
        assert parse_scope_string("read") == ["read"]

    def test_empty_string(self):
        """Test parsing empty string."""
        assert parse_scope_string("") == []

    def test_custom_delimiter(self):
        """Test parsing with custom delimiter."""
        assert parse_scope_string("read,write,admin", delimiter=",") == ["read", "write", "admin"]

    def test_extra_whitespace(self):
        """Test parsing with extra whitespace."""
        assert parse_scope_string("read  write   admin") == ["read", "write", "admin"]

    def test_hierarchical_scopes(self):
        """Test parsing hierarchical scopes."""
        assert parse_scope_string("users:read posts:write") == ["users:read", "posts:write"]
