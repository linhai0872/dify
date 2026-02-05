"""
[CUSTOM] CLI commands for multi-workspace permission control.

Usage:
    flask custom-set-super-admin --email admin@example.com
"""

import click
from sqlalchemy.orm import sessionmaker

from custom.feature_flags import DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED
from custom.models.custom_account_ext import SystemRole
from extensions.ext_database import db
from services.account_service import AccountService


@click.command("custom-set-super-admin", help="[CUSTOM] Set a user as super_admin.")
@click.option("--email", prompt=True, help="Account email to set as super_admin")
def custom_set_super_admin(email: str):
    """
    Set a user as super_admin for multi-workspace permission control.

    This command:
    1. Finds the user by email
    2. Sets their system_role to 'super_admin'
    3. Reports success or failure

    Example:
        flask custom-set-super-admin --email admin@example.com
    """
    if not DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED:
        click.echo(click.style(
            "Error: DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED is not enabled.",
            fg="red"
        ))
        click.echo("Please set DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED=true in your environment.")
        return

    normalized_email = email.strip().lower()

    with sessionmaker(db.engine, expire_on_commit=False).begin() as session:
        account = AccountService.get_account_by_email_with_case_fallback(normalized_email, session=session)

        if not account:
            click.echo(click.style(f"Error: Account not found for email: {email}", fg="red"))
            return

        current_role = getattr(account, "system_role", None) or "normal"

        if current_role == SystemRole.SUPER_ADMIN:
            click.echo(click.style(f"User {email} is already a super_admin.", fg="yellow"))
            return

        # Update the system_role
        account.system_role = SystemRole.SUPER_ADMIN.value

        click.echo(click.style(f"Success! User {email} has been set as super_admin.", fg="green"))
        click.echo(f"  Previous role: {current_role}")
        click.echo(f"  New role: {SystemRole.SUPER_ADMIN.value}")


@click.command("custom-list-super-admins", help="[CUSTOM] List all super_admin users.")
def custom_list_super_admins():
    """
    List all users with super_admin system role.

    Example:
        flask custom-list-super-admins
    """
    if not DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED:
        click.echo(click.style(
            "Error: DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED is not enabled.",
            fg="red"
        ))
        return

    from models.account import Account

    with sessionmaker(db.engine, expire_on_commit=False).begin() as session:
        super_admins = session.query(Account).filter(
            Account.system_role == SystemRole.SUPER_ADMIN.value
        ).all()

        if not super_admins:
            click.echo(click.style("No super_admin users found.", fg="yellow"))
            click.echo("\nTo set a user as super_admin, run:")
            click.echo("  flask custom-set-super-admin --email <email>")
            return

        click.echo(click.style(f"Found {len(super_admins)} super_admin user(s):", fg="green"))
        click.echo()
        for admin in super_admins:
            click.echo(f"  - {admin.email} (ID: {admin.id})")
            click.echo(f"    Name: {admin.name or 'N/A'}")
            click.echo(f"    Status: {admin.status}")
            click.echo()


@click.command("custom-remove-super-admin", help="[CUSTOM] Remove super_admin role from a user.")
@click.option("--email", prompt=True, help="Account email to remove super_admin from")
@click.option("--confirm", is_flag=True, help="Confirm the action")
def custom_remove_super_admin(email: str, confirm: bool):
    """
    Remove super_admin role from a user (set to 'normal').

    Example:
        flask custom-remove-super-admin --email admin@example.com --confirm
    """
    if not DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED:
        click.echo(click.style(
            "Error: DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED is not enabled.",
            fg="red"
        ))
        return

    if not confirm:
        click.echo(click.style("Error: Please add --confirm flag to confirm this action.", fg="red"))
        return

    normalized_email = email.strip().lower()

    with sessionmaker(db.engine, expire_on_commit=False).begin() as session:
        account = AccountService.get_account_by_email_with_case_fallback(normalized_email, session=session)

        if not account:
            click.echo(click.style(f"Error: Account not found for email: {email}", fg="red"))
            return

        current_role = getattr(account, "system_role", None) or "normal"

        if current_role != SystemRole.SUPER_ADMIN:
            click.echo(click.style(f"User {email} is not a super_admin (current role: {current_role}).", fg="yellow"))
            return

        # Check if this is the last super_admin
        from models.account import Account
        super_admin_count = session.query(Account).filter(
            Account.system_role == SystemRole.SUPER_ADMIN.value
        ).count()

        if super_admin_count <= 1:
            click.echo(click.style(
                "Error: Cannot remove the last super_admin. At least one super_admin must exist.",
                fg="red"
            ))
            return

        # Update the system_role
        account.system_role = SystemRole.NORMAL.value

        click.echo(click.style(f"Success! Removed super_admin role from {email}.", fg="green"))
        click.echo(f"  New role: {SystemRole.NORMAL.value}")
