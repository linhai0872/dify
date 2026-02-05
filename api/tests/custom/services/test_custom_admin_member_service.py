"""
[CUSTOM] Tests for CustomAdminMemberService.

Tests the admin member service methods for workspace member management.
"""

from unittest.mock import MagicMock, patch

from custom.services.custom_admin_member_service import CustomAdminMemberService
from models.account import TenantAccountRole


class TestAddMember:
    """Tests for add_member method."""

    @patch("custom.services.custom_admin_member_service.db")
    def test_returns_false_for_invalid_role(self, mock_db):
        """Returns False for invalid workspace role."""
        success, error = CustomAdminMemberService.add_member(
            workspace_id="workspace-1",
            user_id="user-1",
            role="invalid_role",
        )

        assert success is False
        assert "Invalid role" in error

    @patch("custom.services.custom_admin_member_service.db")
    def test_returns_false_when_workspace_not_found(self, mock_db):
        """Returns False when workspace not found."""
        mock_db.session.query.return_value.filter.return_value.first.return_value = None

        success, error = CustomAdminMemberService.add_member(
            workspace_id="nonexistent",
            user_id="user-1",
            role=TenantAccountRole.EDITOR,
        )

        assert success is False
        assert error == "Workspace not found"

    @patch("custom.services.custom_admin_member_service.db")
    def test_returns_false_when_user_not_found(self, mock_db):
        """Returns False when user not found."""
        mock_workspace = MagicMock()
        mock_db.session.query.return_value.filter.return_value.first.side_effect = [
            mock_workspace,  # First call: workspace
            None,  # Second call: user
        ]

        success, error = CustomAdminMemberService.add_member(
            workspace_id="workspace-1",
            user_id="nonexistent",
            role=TenantAccountRole.EDITOR,
        )

        assert success is False
        assert error == "User not found"

    @patch("custom.services.custom_admin_member_service.db")
    def test_returns_false_when_already_member(self, mock_db):
        """Returns False when user is already a member."""
        mock_workspace = MagicMock()
        mock_user = MagicMock()
        mock_existing_join = MagicMock()

        # Setup sequential returns for filter().first()
        mock_db.session.query.return_value.filter.return_value.first.side_effect = [
            mock_workspace,  # workspace query
            mock_user,  # user query
            mock_existing_join,  # existing membership query
        ]

        success, error = CustomAdminMemberService.add_member(
            workspace_id="workspace-1",
            user_id="user-1",
            role=TenantAccountRole.EDITOR,
        )

        assert success is False
        assert "already a member" in error


class TestUpdateMemberRole:
    """Tests for update_member_role method."""

    @patch("custom.services.custom_admin_member_service.db")
    def test_returns_false_for_invalid_role(self, mock_db):
        """Returns False for invalid workspace role."""
        success, error = CustomAdminMemberService.update_member_role(
            workspace_id="workspace-1",
            user_id="user-1",
            new_role="invalid_role",
        )

        assert success is False
        assert "Invalid role" in error

    @patch("custom.services.custom_admin_member_service.db")
    def test_returns_false_when_not_member(self, mock_db):
        """Returns False when user is not a member."""
        mock_db.session.query.return_value.filter.return_value.first.return_value = None

        success, error = CustomAdminMemberService.update_member_role(
            workspace_id="workspace-1",
            user_id="user-1",
            new_role=TenantAccountRole.ADMIN,
        )

        assert success is False
        assert "not a member" in error

    @patch("custom.services.custom_admin_member_service.db")
    def test_prevents_removing_last_owner(self, mock_db):
        """Cannot change role of last owner to non-owner."""
        mock_join = MagicMock()
        mock_join.role = TenantAccountRole.OWNER

        mock_db.session.query.return_value.filter.return_value.first.return_value = mock_join
        mock_db.session.query.return_value.filter.return_value.count.return_value = 1  # Only one owner

        success, error = CustomAdminMemberService.update_member_role(
            workspace_id="workspace-1",
            user_id="user-1",
            new_role=TenantAccountRole.ADMIN,  # Demoting from owner
        )

        assert success is False
        assert "at least one owner" in error

    @patch("custom.services.custom_admin_member_service.db")
    def test_allows_changing_role_with_multiple_owners(self, mock_db):
        """Can change owner role when there are multiple owners."""
        mock_join = MagicMock()
        mock_join.role = TenantAccountRole.OWNER

        mock_db.session.query.return_value.filter.return_value.first.return_value = mock_join
        mock_db.session.query.return_value.filter.return_value.count.return_value = 2  # Multiple owners

        success, error = CustomAdminMemberService.update_member_role(
            workspace_id="workspace-1",
            user_id="user-1",
            new_role=TenantAccountRole.ADMIN,
        )

        assert success is True
        assert error == ""
        assert mock_join.role == TenantAccountRole.ADMIN


class TestRemoveMember:
    """Tests for remove_member method."""

    @patch("custom.services.custom_admin_member_service.db")
    def test_returns_false_when_not_member(self, mock_db):
        """Returns False when user is not a member."""
        mock_db.session.query.return_value.filter.return_value.first.return_value = None

        success, error = CustomAdminMemberService.remove_member(
            workspace_id="workspace-1",
            user_id="user-1",
        )

        assert success is False
        assert "not a member" in error

    @patch("custom.services.custom_admin_member_service.db")
    def test_prevents_removing_last_owner(self, mock_db):
        """Cannot remove the last owner of a workspace."""
        mock_join = MagicMock()
        mock_join.role = TenantAccountRole.OWNER

        mock_db.session.query.return_value.filter.return_value.first.return_value = mock_join
        mock_db.session.query.return_value.filter.return_value.count.return_value = 1  # Only one owner

        success, error = CustomAdminMemberService.remove_member(
            workspace_id="workspace-1",
            user_id="user-1",
        )

        assert success is False
        assert "last owner" in error

    @patch("custom.services.custom_admin_member_service.db")
    def test_allows_removing_non_owner(self, mock_db):
        """Can remove a non-owner member."""
        mock_join = MagicMock()
        mock_join.role = TenantAccountRole.EDITOR

        mock_db.session.query.return_value.filter.return_value.first.return_value = mock_join

        success, error = CustomAdminMemberService.remove_member(
            workspace_id="workspace-1",
            user_id="user-1",
        )

        assert success is True
        assert error == ""
        mock_db.session.delete.assert_called_once_with(mock_join)
        mock_db.session.commit.assert_called_once()


class TestGetWorkspaceRoles:
    """Tests for get_workspace_roles method."""

    def test_returns_all_roles(self):
        """Returns all available workspace roles."""
        roles = CustomAdminMemberService.get_workspace_roles()

        assert len(roles) == 5
        role_values = [r["value"] for r in roles]
        assert TenantAccountRole.OWNER in role_values
        assert TenantAccountRole.ADMIN in role_values
        assert TenantAccountRole.EDITOR in role_values
        assert TenantAccountRole.NORMAL in role_values
        assert TenantAccountRole.DATASET_OPERATOR in role_values

    def test_roles_have_required_fields(self):
        """Each role has value, label, and description."""
        roles = CustomAdminMemberService.get_workspace_roles()

        for role in roles:
            assert "value" in role
            assert "label" in role
            assert "description" in role
