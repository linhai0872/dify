"""
[CUSTOM] Admin User Controller for system-level user management.

Provides API endpoints for super_admin to manage all users in the system.
"""

from flask import request
from flask_restx import Resource, fields
from pydantic import BaseModel, Field

from controllers.console import console_ns
from controllers.console.wraps import account_initialization_required, setup_required
from custom.models.custom_account_ext import SystemRole
from custom.services.custom_admin_user_service import CustomAdminUserService
from custom.wraps.custom_permission_wraps import system_admin_required
from libs.login import current_account_with_tenant, login_required


# Request/Response Models
class AdminUserListQuery(BaseModel):
    page: int = Field(default=1, ge=1, le=99999)
    limit: int = Field(default=20, ge=1, le=100)
    search: str | None = Field(default=None, max_length=100)
    system_role: str | None = Field(default=None)
    status: str | None = Field(default=None)


class UpdateSystemRolePayload(BaseModel):
    system_role: str = Field(..., description="New system role")


class UpdateUserStatusPayload(BaseModel):
    status: str = Field(..., description="New status: 'active' or 'banned'")


class CreateUserPayload(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="User's display name")
    email: str = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=100, description="User's password")
    system_role: str = Field(default="user", description="System role to assign")


class BatchActionPayload(BaseModel):
    user_ids: list[str] = Field(..., min_length=1, max_length=100, description="List of user IDs")
    action: str = Field(..., description="Action to perform: 'enable', 'disable', or 'delete'")


# Response fields
admin_user_fields = {
    "id": fields.String,
    "name": fields.String,
    "email": fields.String,
    "avatar": fields.String,
    "status": fields.String,
    "system_role": fields.String,
    "last_login_at": fields.String,
    "last_active_at": fields.String,
    "created_at": fields.String,
}

admin_user_detail_fields = {
    **admin_user_fields,
    "workspaces": fields.List(fields.Raw),
}


@console_ns.route("/custom/admin/users")
class AdminUserListApi(Resource):
    """API for listing and creating users (system_admin only)."""

    @setup_required
    @login_required
    @account_initialization_required
    @system_admin_required
    def get(self):
        """
        Get paginated list of all users.

        Query params:
        - page: Page number (default 1)
        - limit: Items per page (default 20, max 100)
        - search: Search by name or email
        - system_role: Filter by system role (system_admin/tenant_manager/user)
        - status: Filter by account status
        """
        args = AdminUserListQuery.model_validate(request.args.to_dict())

        users, total = CustomAdminUserService.get_users(
            page=args.page,
            limit=args.limit,
            search=args.search,
            system_role=args.system_role,
            status=args.status,
        )

        return {
            "data": users,
            "page": args.page,
            "limit": args.limit,
            "total": total,
            "has_more": (args.page * args.limit) < total,
        }, 200

    @setup_required
    @login_required
    @account_initialization_required
    @system_admin_required
    def post(self):
        """
        Create a new user account.

        Body:
        - name: User's display name (required)
        - email: User's email address (required)
        - password: User's password (required, min 8 characters)
        - system_role: System role to assign (default: user)
        """
        payload = request.get_json() or {}

        try:
            args = CreateUserPayload.model_validate(payload)
        except Exception as e:
            return {"error": str(e)}, 400

        user, error = CustomAdminUserService.create_user(
            name=args.name,
            email=args.email,
            password=args.password,
            system_role=args.system_role,
        )

        if user is None:
            return {"error": error}, 400

        return {"data": user, "result": "success"}, 201


@console_ns.route("/custom/admin/users/<string:user_id>")
class AdminUserDetailApi(Resource):
    """API for getting and deleting user details (system_admin only)."""

    @setup_required
    @login_required
    @account_initialization_required
    @system_admin_required
    def get(self, user_id: str):
        """Get user details by ID."""
        user = CustomAdminUserService.get_user_by_id(user_id)

        if not user:
            return {"error": "User not found"}, 404

        return {"data": user}, 200

    @setup_required
    @login_required
    @account_initialization_required
    @system_admin_required
    def delete(self, user_id: str):
        """Delete a user account."""
        current_user, _ = current_account_with_tenant()

        success, error = CustomAdminUserService.delete_user(
            user_id=user_id,
            operator_id=current_user.id,
        )

        if not success:
            return {"error": error}, 400

        return {"result": "success"}, 200


@console_ns.route("/custom/admin/users/<string:user_id>/role")
class AdminUserRoleApi(Resource):
    """API for updating user's system role (system_admin only)."""

    @setup_required
    @login_required
    @account_initialization_required
    @system_admin_required
    def put(self, user_id: str):
        """
        Update user's system role.

        Body:
        - system_role: New system role (system_admin/tenant_manager/user)
        """
        current_user, _ = current_account_with_tenant()
        payload = request.get_json() or {}

        try:
            args = UpdateSystemRolePayload.model_validate(payload)
        except Exception as e:
            return {"error": str(e)}, 400

        success, error = CustomAdminUserService.update_system_role(
            user_id=user_id,
            new_role=args.system_role,
            operator_id=current_user.id,
        )

        if not success:
            return {"error": error}, 400

        return {"result": "success"}, 200


@console_ns.route("/custom/admin/users/<string:user_id>/status")
class AdminUserStatusApi(Resource):
    """API for updating user's account status (system_admin only)."""

    @setup_required
    @login_required
    @account_initialization_required
    @system_admin_required
    def put(self, user_id: str):
        """
        Update user's account status.

        Body:
        - status: New status ('active' or 'banned')
        """
        current_user, _ = current_account_with_tenant()
        payload = request.get_json() or {}

        try:
            args = UpdateUserStatusPayload.model_validate(payload)
        except Exception as e:
            return {"error": str(e)}, 400

        success, error = CustomAdminUserService.update_user_status(
            user_id=user_id,
            new_status=args.status,
            operator_id=current_user.id,
        )

        if not success:
            return {"error": error}, 400

        return {"result": "success"}, 200


@console_ns.route("/custom/admin/users/batch")
class AdminUserBatchApi(Resource):
    """API for batch operations on users (system_admin only)."""

    @setup_required
    @login_required
    @account_initialization_required
    @system_admin_required
    def post(self):
        """
        Perform batch action on multiple users.

        Body:
        - user_ids: List of user IDs to operate on
        - action: Action to perform ('enable', 'disable', 'delete')
        """
        current_user, _ = current_account_with_tenant()
        payload = request.get_json() or {}

        try:
            args = BatchActionPayload.model_validate(payload)
        except Exception as e:
            return {"error": str(e)}, 400

        processed, failed, errors = CustomAdminUserService.batch_update_status(
            user_ids=args.user_ids,
            action=args.action,
            operator_id=current_user.id,
        )

        return {
            "result": "success",
            "processed": processed,
            "failed": failed,
            "errors": errors,
        }, 200


@console_ns.route("/custom/admin/system-roles")
class AdminSystemRolesApi(Resource):
    """API for listing available system roles (system_admin only)."""

    @setup_required
    @login_required
    @account_initialization_required
    @system_admin_required
    def get(self):
        """Get list of available system roles."""
        roles = [
            {
                "value": SystemRole.SYSTEM_ADMIN.value,
                "label": "System Admin",
                "description": "Full system access, can manage all workspaces and users",
            },
            {
                "value": SystemRole.TENANT_MANAGER.value,
                "label": "Tenant Manager",
                "description": "Can create and manage own workspaces",
            },
            {
                "value": SystemRole.USER.value,
                "label": "User",
                "description": "Standard user with no special system permissions",
            },
        ]

        return {"roles": roles}, 200


@console_ns.route("/custom/me/system-role")
class CurrentUserSystemRoleApi(Resource):
    """API for getting current user's system role (any logged-in user)."""

    @setup_required
    @login_required
    @account_initialization_required
    def get(self):
        """
        Get current user's system role and feature flag status.

        Returns:
        - system_role: User's system role (super_admin/workspace_admin/normal)
        - multi_workspace_permission_enabled: Whether the feature is enabled
        """
        from custom.feature_flags import DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED
        from custom.services.custom_system_permission_service import CustomSystemPermissionService

        current_user, _ = current_account_with_tenant()

        if not DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED:
            return {
                "system_role": SystemRole.USER.value,
                "multi_workspace_permission_enabled": False,
            }, 200

        system_role = CustomSystemPermissionService.get_system_role(current_user)

        return {
            "system_role": system_role.value if system_role else SystemRole.USER.value,
            "multi_workspace_permission_enabled": True,
        }, 200


@console_ns.route("/custom/feature-flags")
class CustomFeatureFlagsApi(Resource):
    """API for getting custom feature flags (any logged-in user)."""

    @setup_required
    @login_required
    @account_initialization_required
    def get(self):
        """Get custom feature flag status."""
        from custom.feature_flags import DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED

        return {
            "multi_workspace_permission_enabled": DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED,
        }, 200
