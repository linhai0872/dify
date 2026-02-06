"""
[CUSTOM] Admin Workspace Controller for workspace member management.

Provides API endpoints for system_admin and tenant_manager to manage workspaces and members.
system_admin can manage all workspaces; tenant_manager can only manage own workspaces.
"""

from flask import request
from flask_login import current_user
from flask_restx import Resource
from pydantic import BaseModel, Field

from controllers.console import console_ns
from controllers.console.wraps import account_initialization_required, setup_required
from custom.services.custom_admin_member_service import CustomAdminMemberService
from custom.services.custom_system_permission_service import CustomSystemPermissionService
from custom.wraps.custom_permission_wraps import system_admin_required, tenant_manager_or_admin_required
from libs.login import current_account_with_tenant, login_required


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


class CreateWorkspacePayload(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Workspace name")


@console_ns.route("/custom/admin/workspaces")
class AdminWorkspaceListApi(Resource):
    """API for listing and creating workspaces (system_admin sees all, tenant_manager sees own)."""

    @setup_required
    @login_required
    @account_initialization_required
    @tenant_manager_or_admin_required
    def get(self):
        """
        Get paginated list of workspaces with member counts.

        system_admin sees all workspaces; tenant_manager sees only workspaces they created.

        Query params:
        - page: Page number (default 1)
        - limit: Items per page (default 20, max 100)
        - search: Search by workspace name
        """
        args = WorkspaceListQuery.model_validate(request.args.to_dict())
        current_account, _ = current_account_with_tenant()

        if CustomSystemPermissionService.is_system_admin(current_account):
            workspaces, total = CustomAdminMemberService.get_all_workspaces(
                page=args.page,
                limit=args.limit,
                search=args.search,
            )
        else:
            workspaces, total = CustomAdminMemberService.get_own_workspaces(
                account=current_account,
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

    @setup_required
    @login_required
    @account_initialization_required
    @tenant_manager_or_admin_required
    def post(self):
        """
        Create a new workspace.

        Body:
        - name: Workspace name (required, max 100 characters)
        """
        payload = request.get_json() or {}

        try:
            args = CreateWorkspacePayload.model_validate(payload)
        except Exception as e:
            return {"error": str(e)}, 400

        workspace, error = CustomAdminMemberService.create_workspace(
            name=args.name,
            creator_id=str(current_user.id),
        )

        if workspace is None:
            return {"error": error}, 400

        return {"data": workspace, "result": "success"}, 201


@console_ns.route("/custom/admin/workspaces/<string:workspace_id>")
class AdminWorkspaceApi(Resource):
    """API for managing a specific workspace (system_admin or workspace creator)."""

    @setup_required
    @login_required
    @account_initialization_required
    @tenant_manager_or_admin_required
    def delete(self, workspace_id: str):
        """
        Delete a workspace.

        The workspace must have no members to be deleted.
        The default workspace cannot be deleted.
        tenant_manager can only delete workspaces they created.
        """
        current_account, _ = current_account_with_tenant()

        # tenant_manager ownership check
        if not CustomSystemPermissionService.is_system_admin(current_account):
            if not CustomAdminMemberService.is_workspace_creator(workspace_id, str(current_account.id)):
                return {"error": "You can only delete workspaces you created"}, 403

        success, error = CustomAdminMemberService.delete_workspace(
            workspace_id=workspace_id,
        )

        if not success:
            return {"error": error}, 400

        return {"result": "success"}, 200


@console_ns.route("/custom/admin/workspaces/<string:workspace_id>/members")
class AdminWorkspaceMembersApi(Resource):
    """API for managing workspace members (system_admin or workspace creator)."""

    @setup_required
    @login_required
    @account_initialization_required
    @tenant_manager_or_admin_required
    def get(self, workspace_id: str):
        """
        Get paginated list of workspace members.

        tenant_manager can only view members of workspaces they created.

        Query params:
        - page: Page number (default 1)
        - limit: Items per page (default 20, max 100)
        - search: Search by name or email
        """
        current_account, _ = current_account_with_tenant()

        # tenant_manager ownership check
        if not CustomSystemPermissionService.is_system_admin(current_account):
            if not CustomAdminMemberService.is_workspace_creator(workspace_id, str(current_account.id)):
                return {"error": "You can only manage workspaces you created"}, 403

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
    @tenant_manager_or_admin_required
    def post(self, workspace_id: str):
        """
        Add a user to a workspace.

        tenant_manager can only add members to workspaces they created.

        Body:
        - user_id: User account ID
        - role: Workspace role (owner/admin/editor/normal/dataset_operator)
        """
        current_account, _ = current_account_with_tenant()

        # tenant_manager ownership check
        if not CustomSystemPermissionService.is_system_admin(current_account):
            if not CustomAdminMemberService.is_workspace_creator(workspace_id, str(current_account.id)):
                return {"error": "You can only manage workspaces you created"}, 403

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
    """API for managing a specific workspace member (system_admin or workspace creator)."""

    @setup_required
    @login_required
    @account_initialization_required
    @tenant_manager_or_admin_required
    def put(self, workspace_id: str, user_id: str):
        """
        Update a member's role in a workspace.

        tenant_manager can only manage members in workspaces they created.

        Body:
        - role: New workspace role (owner/admin/editor/normal/dataset_operator)
        """
        current_account, _ = current_account_with_tenant()

        # tenant_manager ownership check
        if not CustomSystemPermissionService.is_system_admin(current_account):
            if not CustomAdminMemberService.is_workspace_creator(workspace_id, str(current_account.id)):
                return {"error": "You can only manage workspaces you created"}, 403

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
    @tenant_manager_or_admin_required
    def delete(self, workspace_id: str, user_id: str):
        """
        Remove a member from a workspace.

        tenant_manager can only manage members in workspaces they created.
        """
        current_account, _ = current_account_with_tenant()

        # tenant_manager ownership check
        if not CustomSystemPermissionService.is_system_admin(current_account):
            if not CustomAdminMemberService.is_workspace_creator(workspace_id, str(current_account.id)):
                return {"error": "You can only manage workspaces you created"}, 403

        success, error = CustomAdminMemberService.remove_member(
            workspace_id=workspace_id,
            user_id=user_id,
        )

        if not success:
            return {"error": error}, 400

        return {"result": "success"}, 200


@console_ns.route("/custom/admin/workspaces/<string:workspace_id>/available-users")
class AdminWorkspaceAvailableUsersApi(Resource):
    """API for getting users that can be added to a workspace."""

    @setup_required
    @login_required
    @account_initialization_required
    @tenant_manager_or_admin_required
    def get(self, workspace_id: str):
        """
        Get users that are not members of this workspace.

        tenant_manager can only access this for workspaces they created.

        Query params:
        - search: Search by name or email
        - limit: Maximum results (default 20, max 50)
        """
        current_account, _ = current_account_with_tenant()

        # tenant_manager ownership check
        if not CustomSystemPermissionService.is_system_admin(current_account):
            if not CustomAdminMemberService.is_workspace_creator(workspace_id, str(current_account.id)):
                return {"error": "You can only manage workspaces you created"}, 403

        args = AvailableUsersQuery.model_validate(request.args.to_dict())

        users = CustomAdminMemberService.get_available_users(
            workspace_id=workspace_id,
            search=args.search,
            limit=args.limit,
        )

        return {"data": users}, 200


@console_ns.route("/custom/admin/workspace-roles")
class AdminWorkspaceRolesApi(Resource):
    """API for listing available workspace roles."""

    @setup_required
    @login_required
    @account_initialization_required
    @tenant_manager_or_admin_required
    def get(self):
        """Get list of available workspace roles."""
        roles = CustomAdminMemberService.get_workspace_roles()
        return {"data": roles}, 200
