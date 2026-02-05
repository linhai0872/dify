"""
[CUSTOM] System-level role enumeration for multi-workspace permission control.

This module defines the SystemRole enum which represents system-level roles
that are independent of workspace-level roles (TenantAccountRole).

System roles control cross-workspace permissions:
- super_admin: Full system access, can manage all workspaces and users
- workspace_admin: Can manage assigned workspaces (future use)
- normal: Default role, standard user with no special system permissions
"""

from enum import StrEnum
from typing import Optional


class SystemRole(StrEnum):
    """System-level role for cross-workspace permission control."""

    SUPER_ADMIN = "super_admin"
    """
    Super administrator with full system access:
    - Can view all workspaces in the system
    - Can manage all users (view, disable, modify roles)
    - Can assign users to any workspace with any workspace role
    """

    WORKSPACE_ADMIN = "workspace_admin"
    """
    Workspace administrator (reserved for future use):
    - Currently has same permissions as normal user
    - Intended for users who manage multiple specific workspaces
    """

    NORMAL = "normal"
    """
    Normal user (default):
    - Can only access workspaces they have joined
    - No special system-level permissions
    """

    @staticmethod
    def is_valid_role(role: str) -> bool:
        """Check if a string is a valid system role."""
        if not role:
            return False
        return role in {
            SystemRole.SUPER_ADMIN,
            SystemRole.WORKSPACE_ADMIN,
            SystemRole.NORMAL,
        }

    @staticmethod
    def is_super_admin(role: Optional["SystemRole"]) -> bool:
        """Check if the role is super_admin."""
        return role == SystemRole.SUPER_ADMIN

    @staticmethod
    def can_access_all_workspaces(role: Optional["SystemRole"]) -> bool:
        """Check if the role grants access to all workspaces."""
        return role == SystemRole.SUPER_ADMIN

    @staticmethod
    def can_manage_users(role: Optional["SystemRole"]) -> bool:
        """Check if the role grants user management permissions."""
        return role == SystemRole.SUPER_ADMIN

    @staticmethod
    def can_assign_members(role: Optional["SystemRole"]) -> bool:
        """Check if the role grants member assignment permissions."""
        return role == SystemRole.SUPER_ADMIN
