"""
[CUSTOM] System Permission Service for multi-workspace permission control.

This service provides methods to check system-level permissions and retrieve
accessible workspaces based on a user's system role.
"""

from typing import Optional

from custom.feature_flags import DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED
from custom.models.custom_account_ext import SystemRole
from extensions.ext_database import db
from models.account import Account, Tenant, TenantAccountJoin, TenantAccountRole, TenantStatus


class CustomSystemPermissionService:
    """Service for system-level permission checks and workspace access control."""

    @staticmethod
    def get_system_role(account: Account) -> SystemRole:
        """
        Get the system role of an account.

        If the feature flag is disabled, returns NORMAL for all users.

        Args:
            account: The account to check

        Returns:
            The account's SystemRole
        """
        if not DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED:
            return SystemRole.NORMAL

        # Get system_role from database
        # Note: system_role field will be added by migration
        system_role_str = getattr(account, "system_role", "normal")
        if system_role_str and SystemRole.is_valid_role(system_role_str):
            return SystemRole(system_role_str)
        return SystemRole.NORMAL

    @staticmethod
    def is_super_admin(account: Account) -> bool:
        """
        Check if an account has super_admin system role.

        Args:
            account: The account to check

        Returns:
            True if the account is a super_admin, False otherwise
        """
        return CustomSystemPermissionService.get_system_role(account) == SystemRole.SUPER_ADMIN

    @staticmethod
    def can_access_all_workspaces(account: Account) -> bool:
        """
        Check if an account can access all workspaces in the system.

        Currently only super_admin has this permission.

        Args:
            account: The account to check

        Returns:
            True if the account can access all workspaces
        """
        if not DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED:
            return False
        return SystemRole.can_access_all_workspaces(
            CustomSystemPermissionService.get_system_role(account)
        )

    @staticmethod
    def can_manage_users(account: Account) -> bool:
        """
        Check if an account can manage users (view, disable, modify roles).

        Args:
            account: The account to check

        Returns:
            True if the account can manage users
        """
        if not DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED:
            return False
        return SystemRole.can_manage_users(
            CustomSystemPermissionService.get_system_role(account)
        )

    @staticmethod
    def can_assign_members(account: Account) -> bool:
        """
        Check if an account can assign members to any workspace.

        Args:
            account: The account to check

        Returns:
            True if the account can assign members
        """
        if not DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED:
            return False
        return SystemRole.can_assign_members(
            CustomSystemPermissionService.get_system_role(account)
        )

    @staticmethod
    def get_accessible_workspaces(account: Account) -> list[dict]:
        """
        Get all workspaces accessible to an account.

        For super_admin: returns all workspaces in the system
        For others: returns only workspaces the user has joined

        Each workspace includes the user's role in that workspace (None if not joined).

        Args:
            account: The account to check

        Returns:
            List of workspace dicts with 'tenant' and 'role' keys
        """
        if CustomSystemPermissionService.can_access_all_workspaces(account):
            return CustomSystemPermissionService._get_all_workspaces_with_role(account)
        else:
            return CustomSystemPermissionService._get_joined_workspaces_with_role(account)

    @staticmethod
    def _get_all_workspaces_with_role(account: Account) -> list[dict]:
        """
        Get all workspaces with the user's role in each.

        Returns all active workspaces. For workspaces the user has joined,
        includes their role; for others, role is None.
        """
        # Get all active workspaces
        all_tenants = db.session.query(Tenant).filter(
            Tenant.status == TenantStatus.NORMAL
        ).all()

        # Get user's joined workspaces with roles
        joined_query = (
            db.session.query(TenantAccountJoin)
            .filter(TenantAccountJoin.account_id == account.id)
        )
        joined_map = {taj.tenant_id: taj.role for taj in joined_query}

        result = []
        for tenant in all_tenants:
            role = joined_map.get(tenant.id)
            result.append({
                "tenant": tenant,
                "role": TenantAccountRole(role) if role else None,
            })

        return result

    @staticmethod
    def _get_joined_workspaces_with_role(account: Account) -> list[dict]:
        """
        Get only the workspaces the user has joined, with their role.
        """
        query = (
            db.session.query(Tenant, TenantAccountJoin)
            .join(TenantAccountJoin, Tenant.id == TenantAccountJoin.tenant_id)
            .filter(
                TenantAccountJoin.account_id == account.id,
                Tenant.status == TenantStatus.NORMAL,
            )
        )

        result = []
        for tenant, taj in query:
            result.append({
                "tenant": tenant,
                "role": TenantAccountRole(taj.role) if taj.role else None,
            })

        return result

    @staticmethod
    def get_user_role_in_workspace(
        account: Account, tenant_id: str
    ) -> Optional[TenantAccountRole]:
        """
        Get the user's role in a specific workspace.

        Args:
            account: The account to check
            tenant_id: The workspace ID

        Returns:
            The user's TenantAccountRole in the workspace, or None if not a member
        """
        taj = (
            db.session.query(TenantAccountJoin)
            .filter(
                TenantAccountJoin.account_id == account.id,
                TenantAccountJoin.tenant_id == tenant_id,
            )
            .first()
        )
        return TenantAccountRole(taj.role) if taj else None

    @staticmethod
    def update_system_role(account_id: str, new_role: SystemRole) -> bool:
        """
        Update an account's system role.

        Args:
            account_id: The account ID to update
            new_role: The new system role

        Returns:
            True if successful, False if account not found
        """
        if not DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED:
            return False

        account = db.session.query(Account).filter(Account.id == account_id).first()
        if not account:
            return False

        # Update system_role (will work after migration adds the field)
        account.system_role = new_role.value
        db.session.commit()
        return True
