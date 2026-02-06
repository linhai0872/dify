"""
[CUSTOM] Tests for SystemRole enum.

Tests the SystemRole enumeration and its helper methods for
multi-workspace permission control.
"""

import pytest

from custom.models.custom_account_ext import SystemRole


class TestSystemRoleEnum:
    """Tests for SystemRole enum values."""

    def test_enum_values(self):
        """Test that enum has expected values."""
        assert SystemRole.SYSTEM_ADMIN == "system_admin"
        assert SystemRole.TENANT_MANAGER == "tenant_manager"
        assert SystemRole.USER == "user"

    def test_enum_count(self):
        """Test that there are exactly 3 system roles."""
        assert len(SystemRole) == 3


class TestIsValidRole:
    """Tests for is_valid_role static method."""

    @pytest.mark.parametrize(
        ("role", "expected"),
        [
            ("system_admin", True),
            ("tenant_manager", True),
            ("user", True),
            (SystemRole.SYSTEM_ADMIN, True),
            (SystemRole.TENANT_MANAGER, True),
            (SystemRole.USER, True),
        ],
    )
    def test_valid_roles(self, role: str, expected: bool):
        """Test that valid role strings are recognized."""
        assert SystemRole.is_valid_role(role) == expected

    @pytest.mark.parametrize(
        "role",
        [
            "admin",
            "owner",
            "editor",
            "invalid",
            "",
            None,
            "SYSTEM_ADMIN",  # Case sensitive
            "System_Admin",
        ],
    )
    def test_invalid_roles(self, role):
        """Test that invalid role strings are rejected."""
        assert SystemRole.is_valid_role(role) is False


class TestIsSystemAdmin:
    """Tests for is_system_admin static method."""

    def test_system_admin_role(self):
        """Test that system_admin role returns True."""
        assert SystemRole.is_system_admin(SystemRole.SYSTEM_ADMIN) is True

    @pytest.mark.parametrize(
        "role",
        [
            SystemRole.TENANT_MANAGER,
            SystemRole.USER,
            None,
        ],
    )
    def test_non_system_admin_roles(self, role):
        """Test that non-system_admin roles return False."""
        assert SystemRole.is_system_admin(role) is False


class TestCanAccessAllWorkspaces:
    """Tests for can_access_all_workspaces static method."""

    def test_system_admin_can_access_all(self):
        """Test that system_admin can access all workspaces."""
        assert SystemRole.can_access_all_workspaces(SystemRole.SYSTEM_ADMIN) is True

    @pytest.mark.parametrize(
        "role",
        [
            SystemRole.TENANT_MANAGER,
            SystemRole.USER,
            None,
        ],
    )
    def test_others_cannot_access_all(self, role):
        """Test that other roles cannot access all workspaces."""
        assert SystemRole.can_access_all_workspaces(role) is False


class TestCanManageUsers:
    """Tests for can_manage_users static method."""

    def test_system_admin_can_manage_users(self):
        """Test that system_admin can manage users."""
        assert SystemRole.can_manage_users(SystemRole.SYSTEM_ADMIN) is True

    @pytest.mark.parametrize(
        "role",
        [
            SystemRole.TENANT_MANAGER,
            SystemRole.USER,
            None,
        ],
    )
    def test_others_cannot_manage_users(self, role):
        """Test that other roles cannot manage users."""
        assert SystemRole.can_manage_users(role) is False


class TestCanAssignMembers:
    """Tests for can_assign_members static method."""

    def test_system_admin_can_assign_members(self):
        """Test that system_admin can assign members to workspaces."""
        assert SystemRole.can_assign_members(SystemRole.SYSTEM_ADMIN) is True

    @pytest.mark.parametrize(
        "role",
        [
            SystemRole.TENANT_MANAGER,
            SystemRole.USER,
            None,
        ],
    )
    def test_others_cannot_assign_members(self, role):
        """Test that other roles cannot assign members to workspaces."""
        assert SystemRole.can_assign_members(role) is False
