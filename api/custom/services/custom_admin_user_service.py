"""
[CUSTOM] Admin User Service for system-level user management.

This service provides methods for super_admin to manage all users in the system,
including listing users, modifying system roles, and changing user status.
"""

from typing import Optional

from sqlalchemy import or_

from custom.feature_flags import DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED
from custom.models.custom_account_ext import SystemRole
from extensions.ext_database import db
from models.account import Account, AccountStatus, Tenant, TenantAccountJoin


class CustomAdminUserService:
    """Service for system-level user management by super_admin."""

    @staticmethod
    def get_users(
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        system_role: Optional[str] = None,
        status: Optional[str] = None,
    ) -> tuple[list[dict], int]:
        """
        Get paginated list of all users.

        Args:
            page: Page number (1-indexed)
            limit: Items per page
            search: Search term for name or email
            system_role: Filter by system role
            status: Filter by account status

        Returns:
            Tuple of (user_list, total_count)
        """
        query = db.session.query(Account)

        # Apply filters
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Account.name.ilike(search_pattern),
                    Account.email.ilike(search_pattern),
                )
            )

        if system_role and SystemRole.is_valid_role(system_role):
            query = query.filter(Account.system_role == system_role)

        if status:
            query = query.filter(Account.status == status)

        # Get total count
        total = query.count()

        # Apply pagination
        users = (
            query.order_by(Account.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        # Build response with workspace info
        user_list = []
        for user in users:
            user_dict = CustomAdminUserService._build_user_dict(user)
            user_list.append(user_dict)

        return user_list, total

    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[dict]:
        """
        Get user details by ID.

        Args:
            user_id: The user's account ID

        Returns:
            User dict with workspace info, or None if not found
        """
        user = db.session.query(Account).filter(Account.id == user_id).first()
        if not user:
            return None

        return CustomAdminUserService._build_user_dict(user, include_workspaces=True)

    @staticmethod
    def update_system_role(
        user_id: str,
        new_role: str,
        operator_id: str,
    ) -> tuple[bool, str]:
        """
        Update a user's system role.

        Args:
            user_id: The user's account ID
            new_role: The new system role
            operator_id: The operator's account ID (for self-demotion check)

        Returns:
            Tuple of (success, error_message)
        """
        if not DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED:
            return False, "Feature not enabled"

        if not SystemRole.is_valid_role(new_role):
            return False, f"Invalid system role: {new_role}"

        user = db.session.query(Account).filter(Account.id == user_id).first()
        if not user:
            return False, "User not found"

        # Prevent self-demotion from super_admin
        if user_id == operator_id and new_role != SystemRole.SUPER_ADMIN:
            current_role = getattr(user, "system_role", "normal")
            if current_role == SystemRole.SUPER_ADMIN:
                return False, "Cannot demote yourself from super_admin"

        # Update the role
        user.system_role = new_role
        db.session.commit()

        return True, ""

    @staticmethod
    def update_user_status(
        user_id: str,
        new_status: str,
        operator_id: str,
    ) -> tuple[bool, str]:
        """
        Update a user's account status (enable/disable).

        Args:
            user_id: The user's account ID
            new_status: The new status ('active' or 'banned')
            operator_id: The operator's account ID (for self-disable check)

        Returns:
            Tuple of (success, error_message)
        """
        if new_status not in (AccountStatus.ACTIVE.value, AccountStatus.BANNED.value):
            return False, f"Invalid status: {new_status}. Must be 'active' or 'banned'"

        user = db.session.query(Account).filter(Account.id == user_id).first()
        if not user:
            return False, "User not found"

        # Prevent self-disable
        if user_id == operator_id and new_status == AccountStatus.BANNED.value:
            return False, "Cannot disable your own account"

        # Update the status
        user.status = new_status
        db.session.commit()

        return True, ""

    @staticmethod
    def _build_user_dict(user: Account, include_workspaces: bool = False) -> dict:
        """Build a user dictionary from an Account object."""
        system_role = getattr(user, "system_role", None) or SystemRole.NORMAL.value

        user_dict = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "avatar": user.avatar,
            "status": user.status,
            "system_role": system_role,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "last_active_at": user.last_active_at.isoformat() if user.last_active_at else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }

        if include_workspaces:
            user_dict["workspaces"] = CustomAdminUserService._get_user_workspaces(user.id)

        return user_dict

    @staticmethod
    def _get_user_workspaces(user_id: str) -> list[dict]:
        """Get list of workspaces a user belongs to."""
        joins = (
            db.session.query(TenantAccountJoin, Tenant)
            .join(Tenant, TenantAccountJoin.tenant_id == Tenant.id)
            .filter(TenantAccountJoin.account_id == user_id)
            .all()
        )

        workspaces = []
        for join, tenant in joins:
            workspaces.append({
                "id": tenant.id,
                "name": tenant.name,
                "role": join.role,
                "current": join.current,
            })

        return workspaces
