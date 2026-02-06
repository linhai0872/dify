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
    def test_returns_user_when_feature_disabled(self):
        """When feature is disabled, always return USER."""
        account = MagicMock()
        account.system_role = "system_admin"

        result = CustomSystemPermissionService.get_system_role(account)

        assert result == SystemRole.USER

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    def test_returns_system_admin_role(self):
        """Returns system_admin when account has that role."""
        account = MagicMock()
        account.system_role = "system_admin"

        result = CustomSystemPermissionService.get_system_role(account)

        assert result == SystemRole.SYSTEM_ADMIN

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    def test_returns_tenant_manager_role(self):
        """Returns tenant_manager when account has that role."""
        account = MagicMock()
        account.system_role = "tenant_manager"

        result = CustomSystemPermissionService.get_system_role(account)

        assert result == SystemRole.TENANT_MANAGER

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    def test_returns_user_role(self):
        """Returns user when account has that role."""
        account = MagicMock()
        account.system_role = "user"

        result = CustomSystemPermissionService.get_system_role(account)

        assert result == SystemRole.USER

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    def test_returns_user_for_invalid_role(self):
        """Returns USER when account has invalid role string."""
        account = MagicMock()
        account.system_role = "invalid_role"

        result = CustomSystemPermissionService.get_system_role(account)

        assert result == SystemRole.USER

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    def test_returns_user_when_role_missing(self):
        """Returns USER when account doesn't have system_role attribute."""
        account = MagicMock(spec=[])  # No attributes

        result = CustomSystemPermissionService.get_system_role(account)

        assert result == SystemRole.USER


class TestIsSystemAdmin:
    """Tests for is_system_admin method."""

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    def test_returns_true_for_system_admin(self):
        """Returns True for system_admin account."""
        account = MagicMock()
        account.system_role = "system_admin"

        result = CustomSystemPermissionService.is_system_admin(account)

        assert result is True

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    @pytest.mark.parametrize("role", ["tenant_manager", "user", "invalid"])
    def test_returns_false_for_non_system_admin(self, role: str):
        """Returns False for non-system_admin accounts."""
        account = MagicMock()
        account.system_role = role

        result = CustomSystemPermissionService.is_system_admin(account)

        assert result is False

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", False)
    def test_returns_false_when_feature_disabled(self):
        """Returns False when feature is disabled, even for system_admin."""
        account = MagicMock()
        account.system_role = "system_admin"

        result = CustomSystemPermissionService.is_system_admin(account)

        assert result is False


class TestCanAccessAllWorkspaces:
    """Tests for can_access_all_workspaces method."""

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    def test_system_admin_can_access_all(self):
        """System admin can access all workspaces."""
        account = MagicMock()
        account.system_role = "system_admin"

        result = CustomSystemPermissionService.can_access_all_workspaces(account)

        assert result is True

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    @pytest.mark.parametrize("role", ["tenant_manager", "user"])
    def test_others_cannot_access_all(self, role: str):
        """Non-system_admin cannot access all workspaces."""
        account = MagicMock()
        account.system_role = role

        result = CustomSystemPermissionService.can_access_all_workspaces(account)

        assert result is False

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", False)
    def test_returns_false_when_feature_disabled(self):
        """Returns False when feature is disabled."""
        account = MagicMock()
        account.system_role = "system_admin"

        result = CustomSystemPermissionService.can_access_all_workspaces(account)

        assert result is False


class TestCanManageUsers:
    """Tests for can_manage_users method."""

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    def test_system_admin_can_manage_users(self):
        """System admin can manage users."""
        account = MagicMock()
        account.system_role = "system_admin"

        result = CustomSystemPermissionService.can_manage_users(account)

        assert result is True

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    @pytest.mark.parametrize("role", ["tenant_manager", "user"])
    def test_others_cannot_manage_users(self, role: str):
        """Non-system_admin cannot manage users."""
        account = MagicMock()
        account.system_role = role

        result = CustomSystemPermissionService.can_manage_users(account)

        assert result is False

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", False)
    def test_returns_false_when_feature_disabled(self):
        """Returns False when feature is disabled."""
        account = MagicMock()
        account.system_role = "system_admin"

        result = CustomSystemPermissionService.can_manage_users(account)

        assert result is False


class TestCanAssignMembers:
    """Tests for can_assign_members method."""

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    def test_system_admin_can_assign_members(self):
        """System admin can assign members to any workspace."""
        account = MagicMock()
        account.system_role = "system_admin"

        result = CustomSystemPermissionService.can_assign_members(account)

        assert result is True

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    @pytest.mark.parametrize("role", ["tenant_manager", "user"])
    def test_others_cannot_assign_members(self, role: str):
        """Non-system_admin cannot assign members to any workspace."""
        account = MagicMock()
        account.system_role = role

        result = CustomSystemPermissionService.can_assign_members(account)

        assert result is False

    @patch("custom.services.custom_system_permission_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", False)
    def test_returns_false_when_feature_disabled(self):
        """Returns False when feature is disabled."""
        account = MagicMock()
        account.system_role = "system_admin"

        result = CustomSystemPermissionService.can_assign_members(account)

        assert result is False
