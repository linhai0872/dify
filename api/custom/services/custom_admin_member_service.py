"""
[CUSTOM] Admin Member Service for workspace member management.

This service provides methods for super_admin to manage workspace members,
including listing members, adding/removing members, and changing roles.
"""

from typing import Optional

from sqlalchemy import func

from extensions.ext_database import db
from models.account import Account, AccountStatus, Tenant, TenantAccountJoin, TenantAccountRole, TenantStatus


class CustomAdminMemberService:
    """Service for workspace member management by super_admin."""

    @staticmethod
    def get_all_workspaces(
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
    ) -> tuple[list[dict], int]:
        """
        Get paginated list of all workspaces with member counts.

        Args:
            page: Page number (1-indexed)
            limit: Items per page
            search: Search term for workspace name

        Returns:
            Tuple of (workspace_list, total_count)
        """
        # Build query for workspaces
        query = db.session.query(Tenant).filter(
            Tenant.status == TenantStatus.NORMAL,
        )

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(Tenant.name.ilike(search_pattern))

        # Get total count
        total = query.count()

        # Apply pagination
        workspaces = (
            query.order_by(Tenant.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        # Get member counts for each workspace
        workspace_ids = [w.id for w in workspaces]
        member_counts = {}
        if workspace_ids:
            counts = (
                db.session.query(
                    TenantAccountJoin.tenant_id,
                    func.count(TenantAccountJoin.account_id).label("count"),
                )
                .filter(TenantAccountJoin.tenant_id.in_(workspace_ids))
                .group_by(TenantAccountJoin.tenant_id)
                .all()
            )
            member_counts = {str(tenant_id): count for tenant_id, count in counts}

        result = []
        for workspace in workspaces:
            result.append({
                "id": str(workspace.id),
                "name": workspace.name,
                "status": workspace.status,
                "created_at": workspace.created_at.isoformat() if workspace.created_at else None,
                "member_count": member_counts.get(str(workspace.id), 0),
            })

        return result, total

    @staticmethod
    def get_workspace_members(
        workspace_id: str,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
    ) -> tuple[list[dict], int, Optional[dict]]:
        """
        Get paginated list of workspace members.

        Args:
            workspace_id: The workspace ID
            page: Page number (1-indexed)
            limit: Items per page
            search: Search term for name or email

        Returns:
            Tuple of (member_list, total_count, workspace_info)
            Returns ([], 0, None) if workspace not found
        """
        # Check workspace exists
        workspace = db.session.query(Tenant).filter(
            Tenant.id == workspace_id,
            Tenant.status == TenantStatus.NORMAL,
        ).first()

        if not workspace:
            return [], 0, None

        workspace_info = {
            "id": workspace.id,
            "name": workspace.name,
            "status": workspace.status,
            "created_at": workspace.created_at.isoformat() if workspace.created_at else None,
        }

        # Build query for members
        query = (
            db.session.query(Account, TenantAccountJoin)
            .join(TenantAccountJoin, Account.id == TenantAccountJoin.account_id)
            .filter(TenantAccountJoin.tenant_id == workspace_id)
        )

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                db.or_(
                    Account.name.ilike(search_pattern),
                    Account.email.ilike(search_pattern),
                )
            )

        # Get total count
        total = query.count()

        # Apply pagination
        results = (
            query.order_by(TenantAccountJoin.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        members = []
        for account, join in results:
            members.append({
                "id": account.id,
                "name": account.name,
                "email": account.email,
                "avatar": account.avatar,
                "status": account.status,
                "role": join.role,
                "joined_at": join.created_at.isoformat() if join.created_at else None,
            })

        return members, total, workspace_info

    @staticmethod
    def add_member(
        workspace_id: str,
        user_id: str,
        role: str,
    ) -> tuple[bool, str]:
        """
        Add a user to a workspace.

        Args:
            workspace_id: The workspace ID
            user_id: The user's account ID
            role: The workspace role to assign

        Returns:
            Tuple of (success, error_message)
        """
        if not TenantAccountRole.is_valid_role(role):
            return False, f"Invalid role: {role}"

        # Check workspace exists
        workspace = db.session.query(Tenant).filter(
            Tenant.id == workspace_id,
            Tenant.status == TenantStatus.NORMAL,
        ).first()

        if not workspace:
            return False, "Workspace not found"

        # Check user exists
        user = db.session.query(Account).filter(Account.id == user_id).first()
        if not user:
            return False, "User not found"

        # Check if already a member
        existing = db.session.query(TenantAccountJoin).filter(
            TenantAccountJoin.tenant_id == workspace_id,
            TenantAccountJoin.account_id == user_id,
        ).first()

        if existing:
            return False, "User is already a member of this workspace"

        # Add member
        join = TenantAccountJoin(
            tenant_id=workspace_id,
            account_id=user_id,
            role=role,
            current=False,
        )
        db.session.add(join)
        db.session.commit()

        return True, ""

    @staticmethod
    def update_member_role(
        workspace_id: str,
        user_id: str,
        new_role: str,
    ) -> tuple[bool, str]:
        """
        Update a member's role in a workspace.

        Args:
            workspace_id: The workspace ID
            user_id: The user's account ID
            new_role: The new workspace role

        Returns:
            Tuple of (success, error_message)
        """
        if not TenantAccountRole.is_valid_role(new_role):
            return False, f"Invalid role: {new_role}"

        # Find the membership
        join = db.session.query(TenantAccountJoin).filter(
            TenantAccountJoin.tenant_id == workspace_id,
            TenantAccountJoin.account_id == user_id,
        ).first()

        if not join:
            return False, "User is not a member of this workspace"

        # If changing from owner to non-owner, check if this is the last owner
        if join.role == TenantAccountRole.OWNER and new_role != TenantAccountRole.OWNER:
            owner_count = db.session.query(TenantAccountJoin).filter(
                TenantAccountJoin.tenant_id == workspace_id,
                TenantAccountJoin.role == TenantAccountRole.OWNER,
            ).count()

            if owner_count <= 1:
                return False, "Cannot change role: workspace must have at least one owner"

        join.role = new_role
        db.session.commit()

        return True, ""

    @staticmethod
    def remove_member(
        workspace_id: str,
        user_id: str,
    ) -> tuple[bool, str]:
        """
        Remove a member from a workspace.

        Args:
            workspace_id: The workspace ID
            user_id: The user's account ID

        Returns:
            Tuple of (success, error_message)
        """
        # Find the membership
        join = db.session.query(TenantAccountJoin).filter(
            TenantAccountJoin.tenant_id == workspace_id,
            TenantAccountJoin.account_id == user_id,
        ).first()

        if not join:
            return False, "User is not a member of this workspace"

        # Check if this is the last owner
        if join.role == TenantAccountRole.OWNER:
            owner_count = db.session.query(TenantAccountJoin).filter(
                TenantAccountJoin.tenant_id == workspace_id,
                TenantAccountJoin.role == TenantAccountRole.OWNER,
            ).count()

            if owner_count <= 1:
                return False, "Cannot remove the last owner of a workspace"

        db.session.delete(join)
        db.session.commit()

        return True, ""

    @staticmethod
    def get_available_users(
        workspace_id: str,
        search: Optional[str] = None,
        limit: int = 20,
    ) -> list[dict]:
        """
        Get users that can be added to a workspace (not already members).

        Args:
            workspace_id: The workspace ID
            search: Search term for name or email
            limit: Maximum number of results

        Returns:
            List of user dicts
        """
        # Get IDs of current members
        member_ids = db.session.query(TenantAccountJoin.account_id).filter(
            TenantAccountJoin.tenant_id == workspace_id
        ).subquery()

        # Query for non-members
        query = db.session.query(Account).filter(
            Account.id.notin_(member_ids),
            Account.status == AccountStatus.ACTIVE.value,
        )

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                db.or_(
                    Account.name.ilike(search_pattern),
                    Account.email.ilike(search_pattern),
                )
            )

        users = query.limit(limit).all()

        return [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "avatar": user.avatar,
            }
            for user in users
        ]

    @staticmethod
    def get_workspace_roles() -> list[dict]:
        """Get list of available workspace roles."""
        return [
            {
                "value": TenantAccountRole.OWNER,
                "label": "Owner",
                "description": "Full control of the workspace",
            },
            {
                "value": TenantAccountRole.ADMIN,
                "label": "Admin",
                "description": "Can manage members and settings",
            },
            {
                "value": TenantAccountRole.EDITOR,
                "label": "Editor",
                "description": "Can create and edit apps and datasets",
            },
            {
                "value": TenantAccountRole.NORMAL,
                "label": "Normal",
                "description": "Read-only access",
            },
            {
                "value": TenantAccountRole.DATASET_OPERATOR,
                "label": "Dataset Operator",
                "description": "Can manage datasets only",
            },
        ]
