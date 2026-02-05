"""
[CUSTOM] Extended Tenant Service for multi-workspace permission control.

This service extends the workspace switching functionality to support
super_admin accessing workspaces they haven't joined (read-only mode).
"""

from custom.services.custom_system_permission_service import CustomSystemPermissionService
from extensions.ext_database import db
from models.account import Account, Tenant, TenantAccountJoin, TenantStatus
from services.account_service import TenantService
from services.errors.account import AccountNotLinkTenantError


class CustomTenantServiceExt:
    """Extended tenant service with super_admin support."""

    @staticmethod
    def switch_tenant(account: Account, tenant_id: str) -> tuple[Tenant, bool]:
        """
        Switch the current workspace for the account.

        For super_admin: Can switch to any workspace, even if not a member.
        For others: Uses original TenantService.switch_tenant behavior.

        Args:
            account: The account switching workspaces
            tenant_id: The target workspace ID

        Returns:
            Tuple of (Tenant, is_member) where is_member indicates if user is a member

        Raises:
            AccountNotLinkTenantError: If non-super_admin tries to switch to unjoined workspace
            ValueError: If tenant not found or archived
        """
        # Check if tenant exists and is active
        tenant = db.session.query(Tenant).filter(
            Tenant.id == tenant_id,
            Tenant.status == TenantStatus.NORMAL,
        ).first()

        if not tenant:
            raise ValueError("Tenant not found or archived")

        # Check if user is a member of the workspace
        tenant_account_join = db.session.query(TenantAccountJoin).filter(
            TenantAccountJoin.account_id == account.id,
            TenantAccountJoin.tenant_id == tenant_id,
        ).first()

        is_member = tenant_account_join is not None

        if is_member:
            # User is a member - use normal switch logic
            TenantService.switch_tenant(account, tenant_id)
            return tenant, True

        # User is NOT a member
        if not CustomSystemPermissionService.can_access_all_workspaces(account):
            # Non-super_admin cannot access unjoined workspaces
            raise AccountNotLinkTenantError("Account is not a member of this workspace")

        # Super admin accessing unjoined workspace (read-only mode)
        # Set the tenant without creating a join record
        # The account.role will be None, indicating read-only access
        CustomTenantServiceExt._set_tenant_for_super_admin(account, tenant)
        return tenant, False

    @staticmethod
    def _set_tenant_for_super_admin(account: Account, tenant: Tenant) -> None:
        """
        Set the current tenant for a super_admin without creating a join record.

        This allows super_admin to view the workspace in read-only mode.
        The account.role will be None.
        """
        # Clear current flag on all existing joins for this account
        db.session.query(TenantAccountJoin).filter(
            TenantAccountJoin.account_id == account.id
        ).update({"current": False})

        # Set the tenant directly on the account object
        # Note: This is a transient state - role will be None
        account._current_tenant = tenant
        account.role = None

        db.session.commit()
