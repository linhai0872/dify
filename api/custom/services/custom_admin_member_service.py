"""
[CUSTOM] Admin Member Service for workspace member management.

This service provides methods for super_admin to manage workspace members,
including listing members, adding/removing members, and changing roles.
Also supports workspace creation and deletion.
"""

from typing import Optional

from sqlalchemy import func

from extensions.ext_database import db
from models.account import Account, AccountStatus, Tenant, TenantAccountJoin, TenantAccountRole, TenantStatus


def _escape_like(value: str) -> str:
    """Escape LIKE wildcard characters in user input."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


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
            search_pattern = f"%{_escape_like(search)}%"
            query = query.filter(Tenant.name.ilike(search_pattern, escape="\\"))

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

        # Determine default workspace ID (earliest created) to mark it in the response
        default_workspace_id = None
        earliest = db.session.query(Tenant.id).filter(
            Tenant.status == TenantStatus.NORMAL,
        ).order_by(Tenant.created_at.asc()).first()
        if earliest:
            default_workspace_id = str(earliest[0])

        result = []
        for workspace in workspaces:
            result.append({
                "id": str(workspace.id),
                "name": workspace.name,
                "status": workspace.status,
                "created_at": workspace.created_at.isoformat() if workspace.created_at else None,
                "member_count": member_counts.get(str(workspace.id), 0),
                "is_default": str(workspace.id) == default_workspace_id,
            })

        return result, total

    @staticmethod
    def get_own_workspaces(
        account: Account,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
    ) -> tuple[list[dict], int]:
        """
        Get paginated list of workspaces created by the given account (for tenant_manager).

        This returns workspaces where the user is an owner via TenantAccountJoin,
        which is set when they create a workspace.

        Args:
            account: The account whose workspaces to list
            page: Page number (1-indexed)
            limit: Items per page
            search: Search term for workspace name

        Returns:
            Tuple of (workspace_list, total_count)
        """
        # Get workspace IDs where account is owner
        owner_workspace_ids = (
            db.session.query(TenantAccountJoin.tenant_id)
            .filter(
                TenantAccountJoin.account_id == account.id,
                TenantAccountJoin.role == TenantAccountRole.OWNER,
            )
            .subquery()
        )

        query = db.session.query(Tenant).filter(
            Tenant.id.in_(owner_workspace_ids),
            Tenant.status == TenantStatus.NORMAL,
        )

        if search:
            search_pattern = f"%{_escape_like(search)}%"
            query = query.filter(Tenant.name.ilike(search_pattern, escape="\\"))

        total = query.count()

        workspaces = (
            query.order_by(Tenant.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        # Get member counts
        workspace_ids = [w.id for w in workspaces]
        member_counts: dict[str, int] = {}
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

        # Determine default workspace ID (earliest created) to mark it in the response
        default_workspace_id = None
        earliest = db.session.query(Tenant.id).filter(
            Tenant.status == TenantStatus.NORMAL,
        ).order_by(Tenant.created_at.asc()).first()
        if earliest:
            default_workspace_id = str(earliest[0])

        result = []
        for workspace in workspaces:
            result.append({
                "id": str(workspace.id),
                "name": workspace.name,
                "status": workspace.status,
                "created_at": workspace.created_at.isoformat() if workspace.created_at else None,
                "member_count": member_counts.get(str(workspace.id), 0),
                "is_default": str(workspace.id) == default_workspace_id,
            })

        return result, total

    @staticmethod
    def is_workspace_creator(workspace_id: str, account_id: str) -> bool:
        """
        Check if an account is the creator (owner) of a workspace.

        Args:
            workspace_id: The workspace ID
            account_id: The account ID to check

        Returns:
            True if the account is an owner of the workspace
        """
        return (
            db.session.query(TenantAccountJoin)
            .filter(
                TenantAccountJoin.tenant_id == workspace_id,
                TenantAccountJoin.account_id == account_id,
                TenantAccountJoin.role == TenantAccountRole.OWNER,
            )
            .first()
            is not None
        )

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
            search_pattern = f"%{_escape_like(search)}%"
            query = query.filter(
                db.or_(
                    Account.name.ilike(search_pattern, escape="\\"),
                    Account.email.ilike(search_pattern, escape="\\"),
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
            search_pattern = f"%{_escape_like(search)}%"
            query = query.filter(
                db.or_(
                    Account.name.ilike(search_pattern, escape="\\"),
                    Account.email.ilike(search_pattern, escape="\\"),
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

    @staticmethod
    def create_workspace(
        name: str,
        creator_id: Optional[str] = None,
    ) -> tuple[Optional[dict], str]:
        """
        Create a new workspace.

        Uses Dify's native TenantService to properly initialize workspace
        (encrypt_public_key, plugin upgrade strategy, etc.).

        Args:
            name: The workspace name
            creator_id: The ID of the user creating the workspace (for tracking)

        Returns:
            Tuple of (workspace_dict, error_message)
            workspace_dict is None if creation failed
        """
        from services.account_service import TenantService

        if not name or not name.strip():
            return None, "Workspace name is required"

        name = name.strip()
        if len(name) > 100:
            return None, "Workspace name must be 100 characters or less"

        # Check if workspace with this name already exists
        existing = db.session.query(Tenant).filter(
            Tenant.name == name,
            Tenant.status == TenantStatus.NORMAL,
        ).first()

        if existing:
            return None, "A workspace with this name already exists"

        try:
            # [CUSTOM] Use TenantService.create_tenant to properly initialize workspace
            # (generates encrypt_public_key, creates plugin upgrade strategy, etc.)
            workspace = TenantService.create_tenant(name=name, is_from_dashboard=True)

            # Set created_by if available (for tenant_manager permission tracking)
            if hasattr(workspace, "created_by") and creator_id:
                workspace.created_by = creator_id
                db.session.commit()

            # Add the creator as owner if creator_id is provided
            if creator_id:
                creator = db.session.query(Account).filter(Account.id == creator_id).first()
                if creator:
                    TenantService.create_tenant_member(workspace, creator, role="owner")

            return {
                "id": str(workspace.id),
                "name": workspace.name,
                "status": workspace.status,
                "created_at": workspace.created_at.isoformat() if workspace.created_at else None,
                "member_count": 1 if creator_id else 0,
            }, ""
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def delete_workspace(
        workspace_id: str,
    ) -> tuple[bool, str]:
        """
        Delete a workspace.

        Args:
            workspace_id: The workspace ID to delete

        Returns:
            Tuple of (success, error_message)
        """
        # Find the workspace
        workspace = db.session.query(Tenant).filter(
            Tenant.id == workspace_id,
        ).first()

        if not workspace:
            return False, "Workspace not found"

        # Check if this is the default workspace (first created workspace)
        # The default workspace typically has the earliest created_at
        earliest_workspace = db.session.query(Tenant).filter(
            Tenant.status == TenantStatus.NORMAL,
        ).order_by(Tenant.created_at.asc()).first()

        if earliest_workspace and str(earliest_workspace.id) == str(workspace_id):
            return False, "Cannot delete the default workspace"

        # Check workspace members
        members = db.session.query(TenantAccountJoin).filter(
            TenantAccountJoin.tenant_id == workspace_id,
        ).all()

        member_count = len(members)

        if member_count > 1:
            return False, "Cannot delete workspace with multiple members. Remove other members first."

        try:
            # Auto-remove the last member (owner) if exists
            if member_count == 1:
                db.session.delete(members[0])

            # Soft delete the workspace by changing status
            workspace.status = TenantStatus.ARCHIVE
            db.session.commit()

            return True, ""
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def is_default_workspace(workspace_id: str) -> bool:
        """
        Check if a workspace is the default (first created) workspace.

        Args:
            workspace_id: The workspace ID to check

        Returns:
            True if this is the default workspace
        """
        earliest_workspace = db.session.query(Tenant).filter(
            Tenant.status == TenantStatus.NORMAL,
        ).order_by(Tenant.created_at.asc()).first()

        return earliest_workspace and str(earliest_workspace.id) == str(workspace_id)
