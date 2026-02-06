"""
[CUSTOM] System-level role enumeration for multi-workspace permission control.

This module defines the SystemRole enum which represents system-level roles
that are independent of workspace-level roles (TenantAccountRole).

System roles control cross-workspace permissions:
- system_admin: Full system access, can manage all workspaces and users
- tenant_manager: Can create and manage own workspaces
- user: Default role, standard user with no special system permissions
"""

from enum import StrEnum
from typing import Optional


class SystemRole(StrEnum):
    """System-level role for cross-workspace permission control."""

    SYSTEM_ADMIN = "system_admin"
    """
    System administrator with full system access:
    - Can view all workspaces in the system
    - Can manage all users (view, create, disable, modify roles)
    - Can create/delete any workspace
    - Can assign users to any workspace with any workspace role
    - Cannot demote other system_admin (requires CLI)
    """

    TENANT_MANAGER = "tenant_manager"
    """
    Tenant manager who can manage their own workspaces:
    - Can create new workspaces (becomes owner automatically)
    - Can delete workspaces they created
    - Can manage members in their own workspaces
    - Cannot access system admin interface
    - Cannot view/manage workspaces created by others
    """

    USER = "user"
    """
    Normal user (default):
    - Can only access workspaces they have been invited to
    - No special system-level permissions
    - Cannot create workspaces
    """

    # Legacy aliases for backward compatibility during migration
    # These will be removed after migration is complete
    @classmethod
    def from_legacy(cls, role: str) -> "SystemRole":
        """Convert legacy role names to new names."""
        legacy_map = {
            "super_admin": cls.SYSTEM_ADMIN,
            "workspace_admin": cls.TENANT_MANAGER,
            "normal": cls.USER,
        }
        if role in legacy_map:
            return legacy_map[role]
        return cls(role)

    @staticmethod
    def is_valid_role(role: str) -> bool:
        """Check if a string is a valid system role."""
        if not role:
            return False
        return role in {
            SystemRole.SYSTEM_ADMIN,
            SystemRole.TENANT_MANAGER,
            SystemRole.USER,
        }

    @staticmethod
    def is_system_admin(role: Optional["SystemRole"]) -> bool:
        """Check if the role is system_admin."""
        return role == SystemRole.SYSTEM_ADMIN

    @staticmethod
    def is_tenant_manager(role: Optional["SystemRole"]) -> bool:
        """Check if the role is tenant_manager."""
        return role == SystemRole.TENANT_MANAGER

    @staticmethod
    def can_access_all_workspaces(role: Optional["SystemRole"]) -> bool:
        """Check if the role grants access to all workspaces."""
        return role == SystemRole.SYSTEM_ADMIN

    @staticmethod
    def can_manage_users(role: Optional["SystemRole"]) -> bool:
        """Check if the role grants user management permissions."""
        return role == SystemRole.SYSTEM_ADMIN

    @staticmethod
    def can_assign_members(role: Optional["SystemRole"]) -> bool:
        """Check if the role grants member assignment permissions to any workspace."""
        return role == SystemRole.SYSTEM_ADMIN

    @staticmethod
    def can_create_workspace(role: Optional["SystemRole"]) -> bool:
        """Check if the role can create new workspaces."""
        return role in {SystemRole.SYSTEM_ADMIN, SystemRole.TENANT_MANAGER}

    @staticmethod
    def can_delete_workspace(role: Optional["SystemRole"], is_creator: bool = False) -> bool:
        """Check if the role can delete a workspace.

        Args:
            role: The system role to check
            is_creator: Whether the user is the creator of the workspace

        Returns:
            True if the user can delete the workspace
        """
        if role == SystemRole.SYSTEM_ADMIN:
            return True
        if role == SystemRole.TENANT_MANAGER and is_creator:
            return True
        return False

    # Backward compatibility aliases
    @staticmethod
    def is_super_admin(role: Optional["SystemRole"]) -> bool:
        """Alias for is_system_admin (deprecated, use is_system_admin instead)."""
        return SystemRole.is_system_admin(role)
