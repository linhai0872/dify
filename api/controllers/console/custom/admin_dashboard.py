"""
[CUSTOM] Admin Dashboard Controller for system-level statistics.

Provides API endpoint for system_admin to get dashboard summary stats.
"""

from flask_restx import Resource

from controllers.console import console_ns
from controllers.console.wraps import account_initialization_required, setup_required
from custom.models.custom_account_ext import SystemRole
from custom.wraps.custom_permission_wraps import system_admin_required
from extensions.ext_database import db
from libs.login import login_required
from models.account import Account, AccountStatus, Tenant, TenantStatus


@console_ns.route("/custom/admin/dashboard")
class AdminDashboardApi(Resource):
    """API for dashboard summary statistics (system_admin only)."""

    @setup_required
    @login_required
    @account_initialization_required
    @system_admin_required
    def get(self):
        """
        Get dashboard summary statistics.

        Returns:
        - total_users: Total number of user accounts
        - active_users: Number of active users
        - banned_users: Number of banned users
        - total_workspaces: Number of active workspaces
        """
        total_users = db.session.query(Account).count()

        active_users = (
            db.session.query(Account)
            .filter(Account.status == AccountStatus.ACTIVE.value)
            .count()
        )

        banned_users = (
            db.session.query(Account)
            .filter(Account.status == AccountStatus.BANNED.value)
            .count()
        )

        total_workspaces = (
            db.session.query(Tenant)
            .filter(Tenant.status == TenantStatus.NORMAL)
            .count()
        )

        return {
            "total_users": total_users,
            "active_users": active_users,
            "banned_users": banned_users,
            "total_workspaces": total_workspaces,
        }, 200
