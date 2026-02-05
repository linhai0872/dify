"""
[CUSTOM] Tests for custom CLI commands.

Tests the CLI commands for multi-workspace permission control.
Note: These tests focus on validation logic that doesn't require database access.
Full integration testing of CLI commands should be done manually or in integration tests.
"""

from unittest.mock import patch

from click.testing import CliRunner

from custom.commands import (
    custom_list_super_admins,
    custom_remove_super_admin,
    custom_set_super_admin,
)
from custom.models.custom_account_ext import SystemRole


class TestCustomSetSuperAdmin:
    """Tests for custom-set-super-admin command."""

    @patch("custom.commands.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", False)
    def test_fails_when_feature_disabled(self):
        """Command fails when feature is disabled."""
        runner = CliRunner()
        result = runner.invoke(custom_set_super_admin, ["--email", "test@example.com"])

        assert result.exit_code == 0
        assert "not enabled" in result.output


class TestCustomListSuperAdmins:
    """Tests for custom-list-super-admins command."""

    @patch("custom.commands.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", False)
    def test_fails_when_feature_disabled(self):
        """Command fails when feature is disabled."""
        runner = CliRunner()
        result = runner.invoke(custom_list_super_admins)

        assert "not enabled" in result.output


class TestCustomRemoveSuperAdmin:
    """Tests for custom-remove-super-admin command."""

    @patch("custom.commands.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", False)
    def test_fails_when_feature_disabled(self):
        """Command fails when feature is disabled."""
        runner = CliRunner()
        result = runner.invoke(custom_remove_super_admin, ["--email", "test@example.com", "--confirm"])

        assert "not enabled" in result.output

    @patch("custom.commands.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    def test_fails_without_confirm_flag(self):
        """Command fails without --confirm flag."""
        runner = CliRunner()
        result = runner.invoke(custom_remove_super_admin, ["--email", "test@example.com"])

        assert "add --confirm" in result.output


class TestSystemRoleValidation:
    """Tests for SystemRole validation used by CLI commands."""

    def test_super_admin_role_value(self):
        """SystemRole.SUPER_ADMIN has correct value."""
        assert SystemRole.SUPER_ADMIN.value == "super_admin"

    def test_normal_role_value(self):
        """SystemRole.NORMAL has correct value."""
        assert SystemRole.NORMAL.value == "normal"

    def test_is_valid_role_super_admin(self):
        """is_valid_role returns True for super_admin."""
        assert SystemRole.is_valid_role("super_admin") is True

    def test_is_valid_role_invalid(self):
        """is_valid_role returns False for invalid role."""
        assert SystemRole.is_valid_role("invalid") is False
