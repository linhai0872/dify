"""
[CUSTOM] Tests for CustomSystemPermissionService.

Tests the system permission service methods for multi-workspace permission control.
"""

from unittest.mock import MagicMock, patch

import pytest

from custom.models.custom_account_ext import SystemRole
from custom.services.custom_system_permission_service import CustomSystemPermissionService


class TestGetSystemRole:
    """Tests for get_system_role method."""

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", False)
    def test_returns_normal_when_feature_disabled(self):
        """When feature is disabled, always return NORMAL."""
        account = MagicMock()
        account.system_role = "super_admin"

        result = CustomSystemPermissionService.get_system_role(account)

        assert result == SystemRole.NORMAL

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    def test_returns_super_admin_role(self):
        """Returns super_admin when account has that role."""
        account = MagicMock()
        account.system_role = "super_admin"

        result = CustomSystemPermissionService.get_system_role(account)

        assert result == SystemRole.SUPER_ADMIN

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    def test_returns_workspace_admin_role(self):
        """Returns workspace_admin when account has that role."""
        account = MagicMock()
        account.system_role = "workspace_admin"

        result = CustomSystemPermissionService.get_system_role(account)

        assert result == SystemRole.WORKSPACE_ADMIN

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    def test_returns_normal_role(self):
        """Returns normal when account has that role."""
        account = MagicMock()
        account.system_role = "normal"

        result = CustomSystemPermissionService.get_system_role(account)

        assert result == SystemRole.NORMAL

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    def test_returns_normal_for_invalid_role(self):
        """Returns NORMAL when account has invalid role string."""
        account = MagicMock()
        account.system_role = "invalid_role"

        result = CustomSystemPermissionService.get_system_role(account)

        assert result == SystemRole.NORMAL

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    def test_returns_normal_when_role_missing(self):
        """Returns NORMAL when account doesn't have system_role attribute."""
        account = MagicMock(spec=[])  # No attributes

        result = CustomSystemPermissionService.get_system_role(account)

        assert result == SystemRole.NORMAL


class TestIsSuperAdmin:
    """Tests for is_super_admin method."""

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    def test_returns_true_for_super_admin(self):
        """Returns True for super_admin account."""
        account = MagicMock()
        account.system_role = "super_admin"

        result = CustomSystemPermissionService.is_super_admin(account)

        assert result is True

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    @pytest.mark.parametrize("role", ["workspace_admin", "normal", "invalid"])
    def test_returns_false_for_non_super_admin(self, role: str):
        """Returns False for non-super_admin accounts."""
        account = MagicMock()
        account.system_role = role

        result = CustomSystemPermissionService.is_super_admin(account)

        assert result is False

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", False)
    def test_returns_false_when_feature_disabled(self):
        """Returns False when feature is disabled, even for super_admin."""
        account = MagicMock()
        account.system_role = "super_admin"

        result = CustomSystemPermissionService.is_super_admin(account)

        assert result is False


class TestCanAccessAllWorkspaces:
    """Tests for can_access_all_workspaces method."""

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    def test_super_admin_can_access_all(self):
        """Super admin can access all workspaces."""
        account = MagicMock()
        account.system_role = "super_admin"

        result = CustomSystemPermissionService.can_access_all_workspaces(account)

        assert result is True

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    @pytest.mark.parametrize("role", ["workspace_admin", "normal"])
    def test_others_cannot_access_all(self, role: str):
        """Non-super_admin cannot access all workspaces."""
        account = MagicMock()
        account.system_role = role

        result = CustomSystemPermissionService.can_access_all_workspaces(account)

        assert result is False

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", False)
    def test_returns_false_when_feature_disabled(self):
        """Returns False when feature is disabled."""
        account = MagicMock()
        account.system_role = "super_admin"

        result = CustomSystemPermissionService.can_access_all_workspaces(account)

        assert result is False


class TestCanManageUsers:
    """Tests for can_manage_users method."""

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    def test_super_admin_can_manage_users(self):
        """Super admin can manage users."""
        account = MagicMock()
        account.system_role = "super_admin"

        result = CustomSystemPermissionService.can_manage_users(account)

        assert result is True

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    @pytest.mark.parametrize("role", ["workspace_admin", "normal"])
    def test_others_cannot_manage_users(self, role: str):
        """Non-super_admin cannot manage users."""
        account = MagicMock()
        account.system_role = role

        result = CustomSystemPermissionService.can_manage_users(account)

        assert result is False

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", False)
    def test_returns_false_when_feature_disabled(self):
        """Returns False when feature is disabled."""
        account = MagicMock()
        account.system_role = "super_admin"

        result = CustomSystemPermissionService.can_manage_users(account)

        assert result is False


class TestCanAssignMembers:
    """Tests for can_assign_members method."""

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    def test_super_admin_can_assign_members(self):
        """Super admin can assign members to any workspace."""
        account = MagicMock()
        account.system_role = "super_admin"

        result = CustomSystemPermissionService.can_assign_members(account)

        assert result is True

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    @pytest.mark.parametrize("role", ["workspace_admin", "normal"])
    def test_others_cannot_assign_members(self, role: str):
        """Non-super_admin cannot assign members to any workspace."""
        account = MagicMock()
        account.system_role = role

        result = CustomSystemPermissionService.can_assign_members(account)

        assert result is False

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", False)
    def test_returns_false_when_feature_disabled(self):
        """Returns False when feature is disabled."""
        account = MagicMock()
        account.system_role = "super_admin"

        result = CustomSystemPermissionService.can_assign_members(account)

        assert result is False
