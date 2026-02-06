"""
[CUSTOM] Tests for CustomAdminUserService.

Tests the admin user service methods for user management.
"""

from unittest.mock import MagicMock, patch

from custom.models.custom_account_ext import SystemRole
from custom.services.custom_admin_user_service import CustomAdminUserService
from models.account import AccountStatus


class TestUpdateSystemRole:
    """Tests for update_system_role method."""

    @patch("custom.services.custom_admin_user_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", False)
    @patch("custom.services.custom_admin_user_service.db")
    def test_returns_false_when_feature_disabled(self, mock_db):
        """When feature is disabled, returns False."""
        success, error = CustomAdminUserService.update_system_role(
            user_id="user-1",
            new_role=SystemRole.SYSTEM_ADMIN,
            operator_id="operator-1",
        )

        assert success is False
        assert error == "Feature not enabled"

    @patch("custom.services.custom_admin_user_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    @patch("custom.services.custom_admin_user_service.db")
    def test_returns_false_for_invalid_role(self, mock_db):
        """Returns False for invalid role string."""
        success, error = CustomAdminUserService.update_system_role(
            user_id="user-1",
            new_role="invalid_role",
            operator_id="operator-1",
        )

        assert success is False
        assert "Invalid system role" in error

    @patch("custom.services.custom_admin_user_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    @patch("custom.services.custom_admin_user_service.db")
    def test_returns_false_when_user_not_found(self, mock_db):
        """Returns False when user not found."""
        mock_db.session.query.return_value.filter.return_value.first.return_value = None

        success, error = CustomAdminUserService.update_system_role(
            user_id="nonexistent",
            new_role=SystemRole.USER,
            operator_id="operator-1",
        )

        assert success is False
        assert error == "User not found"

    @patch("custom.services.custom_admin_user_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    @patch("custom.services.custom_admin_user_service.db")
    def test_prevents_self_demotion_from_system_admin(self, mock_db):
        """Cannot demote yourself from system_admin."""
        mock_user = MagicMock()
        mock_user.id = "user-1"
        mock_user.system_role = SystemRole.SYSTEM_ADMIN
        mock_db.session.query.return_value.filter.return_value.first.return_value = mock_user

        success, error = CustomAdminUserService.update_system_role(
            user_id="user-1",
            new_role=SystemRole.USER,
            operator_id="user-1",  # Same as user_id
        )

        assert success is False
        assert "Cannot change your own system_admin role" in error

    @patch("custom.services.custom_admin_user_service.DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", True)
    @patch("custom.services.custom_admin_user_service.db")
    def test_allows_promoting_other_user(self, mock_db):
        """Can promote another user to system_admin."""
        mock_user = MagicMock()
        mock_user.id = "user-2"
        mock_user.system_role = SystemRole.USER
        mock_db.session.query.return_value.filter.return_value.first.return_value = mock_user

        success, error = CustomAdminUserService.update_system_role(
            user_id="user-2",
            new_role=SystemRole.SYSTEM_ADMIN,
            operator_id="user-1",  # Different from user_id
        )

        assert success is True
        assert error == ""
        assert mock_user.system_role == SystemRole.SYSTEM_ADMIN
        mock_db.session.commit.assert_called_once()


class TestUpdateUserStatus:
    """Tests for update_user_status method."""

    @patch("custom.services.custom_admin_user_service.db")
    def test_returns_false_for_invalid_status(self, mock_db):
        """Returns False for invalid status string."""
        success, error = CustomAdminUserService.update_user_status(
            user_id="user-1",
            new_status="invalid_status",
            operator_id="operator-1",
        )

        assert success is False
        assert "Invalid status" in error

    @patch("custom.services.custom_admin_user_service.db")
    def test_returns_false_when_user_not_found(self, mock_db):
        """Returns False when user not found."""
        mock_db.session.query.return_value.filter.return_value.first.return_value = None

        success, error = CustomAdminUserService.update_user_status(
            user_id="nonexistent",
            new_status=AccountStatus.ACTIVE.value,
            operator_id="operator-1",
        )

        assert success is False
        assert error == "User not found"

    @patch("custom.services.custom_admin_user_service.db")
    def test_prevents_self_disable(self, mock_db):
        """Cannot disable your own account."""
        mock_user = MagicMock()
        mock_user.id = "user-1"
        mock_db.session.query.return_value.filter.return_value.first.return_value = mock_user

        success, error = CustomAdminUserService.update_user_status(
            user_id="user-1",
            new_status=AccountStatus.BANNED.value,
            operator_id="user-1",  # Same as user_id
        )

        assert success is False
        assert "Cannot disable your own account" in error

    @patch("custom.services.custom_admin_user_service.db")
    def test_allows_disabling_other_user(self, mock_db):
        """Can disable another user's account."""
        mock_user = MagicMock()
        mock_user.id = "user-2"
        mock_user.status = AccountStatus.ACTIVE.value
        mock_db.session.query.return_value.filter.return_value.first.return_value = mock_user

        success, error = CustomAdminUserService.update_user_status(
            user_id="user-2",
            new_status=AccountStatus.BANNED.value,
            operator_id="user-1",  # Different from user_id
        )

        assert success is True
        assert error == ""
        assert mock_user.status == AccountStatus.BANNED.value
        mock_db.session.commit.assert_called_once()

    @patch("custom.services.custom_admin_user_service.db")
    def test_allows_enabling_user(self, mock_db):
        """Can enable a disabled user's account."""
        mock_user = MagicMock()
        mock_user.id = "user-2"
        mock_user.status = AccountStatus.BANNED.value
        mock_db.session.query.return_value.filter.return_value.first.return_value = mock_user

        success, error = CustomAdminUserService.update_user_status(
            user_id="user-2",
            new_status=AccountStatus.ACTIVE.value,
            operator_id="user-1",
        )

        assert success is True
        assert error == ""
        assert mock_user.status == AccountStatus.ACTIVE.value


class TestBuildUserDict:
    """Tests for _build_user_dict method."""

    def test_builds_basic_user_dict(self):
        """Builds user dict with basic fields."""
        mock_user = MagicMock()
        mock_user.id = "user-1"
        mock_user.name = "Test User"
        mock_user.email = "test@example.com"
        mock_user.avatar = "avatar.png"
        mock_user.status = "active"
        mock_user.system_role = "user"
        mock_user.last_login_at = None
        mock_user.last_active_at = None
        mock_user.created_at = None

        result = CustomAdminUserService._build_user_dict(mock_user)

        assert result["id"] == "user-1"
        assert result["name"] == "Test User"
        assert result["email"] == "test@example.com"
        assert result["system_role"] == "user"

    def test_defaults_to_user_when_system_role_missing(self):
        """Defaults to 'user' when system_role attribute is missing."""
        mock_user = MagicMock(spec=["id", "name", "email", "avatar", "status",
                                     "last_login_at", "last_active_at", "created_at"])
        mock_user.id = "user-1"
        mock_user.name = "Test"
        mock_user.email = "test@example.com"
        mock_user.avatar = None
        mock_user.status = "active"
        mock_user.last_login_at = None
        mock_user.last_active_at = None
        mock_user.created_at = None

        result = CustomAdminUserService._build_user_dict(mock_user)

        assert result["system_role"] == "user"
