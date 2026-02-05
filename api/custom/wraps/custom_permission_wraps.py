"""
[CUSTOM] Permission decorators for multi-workspace permission control.

This module provides decorators to check system-level permissions
on API endpoints.
"""

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from flask import abort

from custom.feature_flags import DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED
from custom.services.custom_system_permission_service import CustomSystemPermissionService
from libs.login import current_account_with_tenant

P = ParamSpec("P")
R = TypeVar("R")


def super_admin_required(view: Callable[P, R]) -> Callable[P, R]:
    """
    Decorator to require super_admin system role for an endpoint.

    Usage:
        @super_admin_required
        def my_admin_endpoint():
            # Only super_admin can access this
            pass

    If the feature flag is disabled, returns 404 (feature not available).
    If the user is not a super_admin, returns 403 Forbidden.
    """

    @wraps(view)
    def decorated(*args: P.args, **kwargs: P.kwargs) -> R:
        # Check if feature is enabled
        if not DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED:
            abort(404, description="Feature not available")

        # Get current user
        current_user, _ = current_account_with_tenant()

        # Check if user is super_admin
        if not CustomSystemPermissionService.is_super_admin(current_user):
            abort(403, description="Super admin permission required")

        return view(*args, **kwargs)

    return decorated


def feature_enabled_required(view: Callable[P, R]) -> Callable[P, R]:
    """
    Decorator to require the multi-workspace permission feature to be enabled.

    Use this for endpoints that should only be available when the feature is on,
    but don't require super_admin permissions.

    If the feature flag is disabled, returns 404 (feature not available).
    """

    @wraps(view)
    def decorated(*args: P.args, **kwargs: P.kwargs) -> R:
        if not DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED:
            abort(404, description="Feature not available")
        return view(*args, **kwargs)

    return decorated
