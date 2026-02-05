"""
[CUSTOM] Admin Workspace Controller for workspace member management.

Provides API endpoints for super_admin to manage workspace members.
"""

from flask import request
from flask_restx import Resource
from pydantic import BaseModel, Field

from controllers.console import console_ns
from controllers.console.wraps import account_initialization_required, setup_required
from custom.services.custom_admin_member_service import CustomAdminMemberService
from custom.wraps.custom_permission_wraps import super_admin_required
from libs.login import login_required


# Request/Response Models
class MemberListQuery(BaseModel):
    page: int = Field(default=1, ge=1, le=99999)
    limit: int = Field(default=20, ge=1, le=100)
    search: str | None = Field(default=None, max_length=100)


class AddMemberPayload(BaseModel):
    user_id: str = Field(..., description="User account ID")
    role: str = Field(..., description="Workspace role")


class UpdateMemberRolePayload(BaseModel):
    role: str = Field(..., description="New workspace role")


class AvailableUsersQuery(BaseModel):
    search: str | None = Field(default=None, max_length=100)
    limit: int = Field(default=20, ge=1, le=50)


class WorkspaceListQuery(BaseModel):
    page: int = Field(default=1, ge=1, le=99999)
    limit: int = Field(default=20, ge=1, le=100)
    search: str | None = Field(default=None, max_length=100)


@console_ns.route("/custom/admin/workspaces")
class AdminWorkspaceListApi(Resource):
    """API for listing all workspaces (super_admin only)."""

    @setup_required
    @login_required
    @account_initialization_required
    @super_admin_required
    def get(self):
        """
        Get paginated list of all workspaces with member counts.

        Query params:
        - page: Page number (default 1)
        - limit: Items per page (default 20, max 100)
        - search: Search by workspace name
        """
        args = WorkspaceListQuery.model_validate(request.args.to_dict())

        workspaces, total = CustomAdminMemberService.get_all_workspaces(
            page=args.page,
            limit=args.limit,
            search=args.search,
        )

        return {
            "data": workspaces,
            "page": args.page,
            "limit": args.limit,
            "total": total,
            "has_more": (args.page * args.limit) < total,
        }, 200


@console_ns.route("/custom/admin/workspaces/<string:workspace_id>/members")
class AdminWorkspaceMembersApi(Resource):
    """API for managing workspace members (super_admin only)."""

    @setup_required
    @login_required
    @account_initialization_required
    @super_admin_required
    def get(self, workspace_id: str):
        """
        Get paginated list of workspace members.

        Query params:
        - page: Page number (default 1)
        - limit: Items per page (default 20, max 100)
        - search: Search by name or email
        """
        args = MemberListQuery.model_validate(request.args.to_dict())

        members, total, workspace = CustomAdminMemberService.get_workspace_members(
            workspace_id=workspace_id,
            page=args.page,
            limit=args.limit,
            search=args.search,
        )

        if workspace is None:
            return {"error": "Workspace not found"}, 404

        return {
            "data": members,
            "workspace": workspace,
            "page": args.page,
            "limit": args.limit,
            "total": total,
            "has_more": (args.page * args.limit) < total,
        }, 200

    @setup_required
    @login_required
    @account_initialization_required
    @super_admin_required
    def post(self, workspace_id: str):
        """
        Add a user to a workspace.

        Body:
        - user_id: User account ID
        - role: Workspace role (owner/admin/editor/normal/dataset_operator)
        """
        payload = request.get_json() or {}

        try:
            args = AddMemberPayload.model_validate(payload)
        except Exception as e:
            return {"error": str(e)}, 400

        success, error = CustomAdminMemberService.add_member(
            workspace_id=workspace_id,
            user_id=args.user_id,
            role=args.role,
        )

        if not success:
            return {"error": error}, 400

        return {"result": "success"}, 201


@console_ns.route("/custom/admin/workspaces/<string:workspace_id>/members/<string:user_id>")
class AdminWorkspaceMemberApi(Resource):
    """API for managing a specific workspace member (super_admin only)."""

    @setup_required
    @login_required
    @account_initialization_required
    @super_admin_required
    def put(self, workspace_id: str, user_id: str):
        """
        Update a member's role in a workspace.

        Body:
        - role: New workspace role (owner/admin/editor/normal/dataset_operator)
        """
        payload = request.get_json() or {}

        try:
            args = UpdateMemberRolePayload.model_validate(payload)
        except Exception as e:
            return {"error": str(e)}, 400

        success, error = CustomAdminMemberService.update_member_role(
            workspace_id=workspace_id,
            user_id=user_id,
            new_role=args.role,
        )

        if not success:
            return {"error": error}, 400

        return {"result": "success"}, 200

    @setup_required
    @login_required
    @account_initialization_required
    @super_admin_required
    def delete(self, workspace_id: str, user_id: str):
        """Remove a member from a workspace."""
        success, error = CustomAdminMemberService.remove_member(
            workspace_id=workspace_id,
            user_id=user_id,
        )

        if not success:
            return {"error": error}, 400

        return {"result": "success"}, 200


@console_ns.route("/custom/admin/workspaces/<string:workspace_id>/available-users")
class AdminWorkspaceAvailableUsersApi(Resource):
    """API for getting users that can be added to a workspace (super_admin only)."""

    @setup_required
    @login_required
    @account_initialization_required
    @super_admin_required
    def get(self, workspace_id: str):
        """
        Get users that are not members of this workspace.

        Query params:
        - search: Search by name or email
        - limit: Maximum results (default 20, max 50)
        """
        args = AvailableUsersQuery.model_validate(request.args.to_dict())

        users = CustomAdminMemberService.get_available_users(
            workspace_id=workspace_id,
            search=args.search,
            limit=args.limit,
        )

        return {"data": users}, 200


@console_ns.route("/custom/admin/workspace-roles")
class AdminWorkspaceRolesApi(Resource):
    """API for listing available workspace roles (super_admin only)."""

    @setup_required
    @login_required
    @account_initialization_required
    @super_admin_required
    def get(self):
        """Get list of available workspace roles."""
        roles = CustomAdminMemberService.get_workspace_roles()
        return {"data": roles}, 200
