"""
[CUSTOM] Admin User Service for system-level user management.

This service provides methods for system_admin to manage all users in the system,
including listing users, modifying system roles, and changing user status.
"""

from typing import Optional

from sqlalchemy import or_

from custom.feature_flags import DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED
from custom.models.custom_account_ext import SystemRole
from extensions.ext_database import db
from models.account import Account, AccountStatus, Tenant, TenantAccountJoin


def _escape_like(value: str) -> str:
    """Escape LIKE wildcard characters in user input."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


class CustomAdminUserService:
    """Service for system-level user management by system_admin."""

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
            search_pattern = f"%{_escape_like(search)}%"
            query = query.filter(
                or_(
                    Account.name.ilike(search_pattern, escape="\\"),
                    Account.email.ilike(search_pattern, escape="\\"),
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
            operator_id: The operator's account ID (for permission checks)

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

        current_role = getattr(user, "system_role", None) or SystemRole.USER.value

        # Prevent self-demotion
        if user_id == operator_id and new_role != current_role:
            if current_role == SystemRole.SYSTEM_ADMIN:
                return False, "Cannot change your own system_admin role"

        # Prevent demoting another system_admin (requires CLI)
        if current_role == SystemRole.SYSTEM_ADMIN and new_role != SystemRole.SYSTEM_ADMIN:
            if user_id != operator_id:
                return False, "Cannot demote other system_admin. Use CLI command instead."

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

        # Prevent disabling other system_admin
        current_role = getattr(user, "system_role", None) or SystemRole.USER.value
        if current_role == SystemRole.SYSTEM_ADMIN and new_status == AccountStatus.BANNED.value:
            if user_id != operator_id:
                return False, "Cannot disable other system_admin"

        # Update the status
        user.status = new_status
        db.session.commit()

        return True, ""

    @staticmethod
    def create_user(
        name: str,
        email: str,
        password: str,
        system_role: str = SystemRole.USER,
    ) -> tuple[Optional[dict], str]:
        """
        Create a new user account.

        Args:
            name: User's display name
            email: User's email address
            password: User's password
            system_role: System role to assign (default: user)

        Returns:
            Tuple of (user_dict, error_message)
        """
        from services.account_service import RegisterService

        # Validate system role
        if not SystemRole.is_valid_role(system_role):
            return None, f"Invalid system role: {system_role}"

        # Check if email already exists
        email = email.strip().lower()
        existing = db.session.query(Account).filter(Account.email == email).first()
        if existing:
            return None, f"Email already exists: {email}"

        try:
            # [CUSTOM] Create account via RegisterService.register with:
            # - is_setup=True: bypass is_allow_register check (admin can always create users)
            # - create_workspace_required=False: don't auto-create workspace for admin-created users
            account = RegisterService.register(
                email=email,
                name=name,
                password=password,
                language="en-US",
                is_setup=True,
                create_workspace_required=False,
            )

            # Update system role
            account.system_role = system_role
            db.session.commit()

            return CustomAdminUserService._build_user_dict(account), ""
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def delete_user(user_id: str, operator_id: str) -> tuple[bool, str]:
        """
        Delete a user account.

        Args:
            user_id: The user's account ID
            operator_id: The operator's account ID

        Returns:
            Tuple of (success, error_message)
        """
        if user_id == operator_id:
            return False, "Cannot delete your own account"

        user = db.session.query(Account).filter(Account.id == user_id).first()
        if not user:
            return False, "User not found"

        # Prevent deleting system_admin
        current_role = getattr(user, "system_role", None) or SystemRole.USER.value
        if current_role == SystemRole.SYSTEM_ADMIN:
            return False, "Cannot delete system_admin. Use CLI command instead."

        try:
            # Remove from all workspaces first
            db.session.query(TenantAccountJoin).filter(
                TenantAccountJoin.account_id == user_id
            ).delete()

            # Delete the account
            db.session.delete(user)
            db.session.commit()

            return True, ""
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def batch_update_status(
        user_ids: list[str],
        action: str,
        operator_id: str,
    ) -> tuple[int, int, list[dict]]:
        """
        Batch update user status using bulk queries to avoid N+1.

        Args:
            user_ids: List of user IDs to update
            action: Action to perform ('enable', 'disable', 'delete')
            operator_id: The operator's account ID

        Returns:
            Tuple of (processed_count, failed_count, errors)
        """
        if action not in ("enable", "disable", "delete"):
            return 0, len(user_ids), [{"id": "all", "error": f"Invalid action: {action}"}]

        # Single query to fetch all target users
        users = db.session.query(Account).filter(Account.id.in_(user_ids)).all()
        users_by_id = {str(u.id): u for u in users}

        errors: list[dict] = []
        eligible_users: list[Account] = []

        # Classify: reject ineligible users, collect eligible ones
        for user_id in user_ids:
            user = users_by_id.get(user_id)
            if not user:
                errors.append({"id": user_id, "error": "User not found"})
                continue
            if user_id == operator_id:
                errors.append({"id": user_id, "error": "Cannot operate on your own account"})
                continue
            current_role = getattr(user, "system_role", None) or SystemRole.USER.value
            if current_role == SystemRole.SYSTEM_ADMIN:
                errors.append({"id": user_id, "error": "Cannot operate on system_admin"})
                continue
            eligible_users.append(user)

        if not eligible_users:
            return 0, len(errors), errors

        eligible_ids = [str(u.id) for u in eligible_users]

        try:
            if action in ("enable", "disable"):
                new_status = AccountStatus.ACTIVE.value if action == "enable" else AccountStatus.BANNED.value
                db.session.query(Account).filter(
                    Account.id.in_(eligible_ids),
                ).update({"status": new_status}, synchronize_session="fetch")
            else:  # delete
                # Bulk remove from all workspaces first
                db.session.query(TenantAccountJoin).filter(
                    TenantAccountJoin.account_id.in_(eligible_ids),
                ).delete(synchronize_session="fetch")
                # Bulk delete accounts
                db.session.query(Account).filter(
                    Account.id.in_(eligible_ids),
                ).delete(synchronize_session="fetch")

            db.session.commit()
            return len(eligible_users), len(errors), errors
        except Exception as e:
            db.session.rollback()
            return 0, len(user_ids), [{"id": "all", "error": str(e)}]

    @staticmethod
    def _build_user_dict(user: Account, include_workspaces: bool = False) -> dict:
        """Build a user dictionary from an Account object."""
        system_role = getattr(user, "system_role", None) or SystemRole.USER.value

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
