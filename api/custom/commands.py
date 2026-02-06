"""
[CUSTOM] CLI commands for multi-workspace permission control.

Usage:
    flask custom-set-system-admin --email admin@example.com
    flask custom-list-system-admins
    flask custom-remove-system-admin --email admin@example.com --confirm
"""

import click
from sqlalchemy.orm import sessionmaker

from custom.feature_flags import DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED
from custom.models.custom_account_ext import SystemRole
from extensions.ext_database import db
from services.account_service import AccountService


@click.command("custom-set-system-admin", help="[CUSTOM] Set a user as system_admin.")
@click.option("--email", prompt=True, help="Account email to set as system_admin")
def custom_set_system_admin(email: str):
    """
    Set a user as system_admin for multi-workspace permission control.

    This command:
    1. Finds the user by email
    2. Sets their system_role to 'system_admin'
    3. Reports success or failure

    Example:
        flask custom-set-system-admin --email admin@example.com
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

        current_role = getattr(account, "system_role", None) or "user"

        if current_role == SystemRole.SYSTEM_ADMIN:
            click.echo(click.style(f"User {email} is already a system_admin.", fg="yellow"))
            return

        # Update the system_role
        account.system_role = SystemRole.SYSTEM_ADMIN.value

        click.echo(click.style(f"Success! User {email} has been set as system_admin.", fg="green"))
        click.echo(f"  Previous role: {current_role}")
        click.echo(f"  New role: {SystemRole.SYSTEM_ADMIN.value}")


# Backward compatibility alias
@click.command("custom-set-super-admin", help="[CUSTOM] Alias for custom-set-system-admin (deprecated).")
@click.option("--email", prompt=True, help="Account email to set as system_admin")
def custom_set_super_admin(email: str):
    """Deprecated alias for custom_set_system_admin."""
    click.echo(click.style(
        "Warning: 'custom-set-super-admin' is deprecated. Use 'custom-set-system-admin' instead.",
        fg="yellow"
    ))
    # Invoke the new command's callback directly to bypass Click parsing
    custom_set_system_admin.callback(email)


@click.command("custom-list-system-admins", help="[CUSTOM] List all system_admin users.")
def custom_list_system_admins():
    """
    List all users with system_admin system role.

    Example:
        flask custom-list-system-admins
    """
    if not DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED:
        click.echo(click.style(
            "Error: DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED is not enabled.",
            fg="red"
        ))
        return

    from models.account import Account

    with sessionmaker(db.engine, expire_on_commit=False).begin() as session:
        system_admins = session.query(Account).filter(
            Account.system_role == SystemRole.SYSTEM_ADMIN.value
        ).all()

        if not system_admins:
            click.echo(click.style("No system_admin users found.", fg="yellow"))
            click.echo("\nTo set a user as system_admin, run:")
            click.echo("  flask custom-set-system-admin --email <email>")
            return

        click.echo(click.style(f"Found {len(system_admins)} system_admin user(s):", fg="green"))
        click.echo()
        for admin in system_admins:
            click.echo(f"  - {admin.email} (ID: {admin.id})")
            click.echo(f"    Name: {admin.name or 'N/A'}")
            click.echo(f"    Status: {admin.status}")
            click.echo()


# Backward compatibility alias
@click.command("custom-list-super-admins", help="[CUSTOM] Alias for custom-list-system-admins (deprecated).")
def custom_list_super_admins():
    """Deprecated alias for custom_list_system_admins."""
    click.echo(click.style(
        "Warning: 'custom-list-super-admins' is deprecated. Use 'custom-list-system-admins' instead.",
        fg="yellow"
    ))
    # Invoke the new command's callback directly to bypass Click parsing
    custom_list_system_admins.callback()


@click.command("custom-remove-system-admin", help="[CUSTOM] Remove system_admin role from a user.")
@click.option("--email", prompt=True, help="Account email to remove system_admin from")
@click.option("--confirm", is_flag=True, help="Confirm the action")
def custom_remove_system_admin(email: str, confirm: bool):
    """
    Remove system_admin role from a user (set to 'user').

    Example:
        flask custom-remove-system-admin --email admin@example.com --confirm
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

        current_role = getattr(account, "system_role", None) or "user"

        if current_role != SystemRole.SYSTEM_ADMIN:
            click.echo(click.style(f"User {email} is not a system_admin (current role: {current_role}).", fg="yellow"))
            return

        # Check if this is the last system_admin
        from models.account import Account
        system_admin_count = session.query(Account).filter(
            Account.system_role == SystemRole.SYSTEM_ADMIN.value
        ).count()

        if system_admin_count <= 1:
            click.echo(click.style(
                "Error: Cannot remove the last system_admin. At least one system_admin must exist.",
                fg="red"
            ))
            return

        # Update the system_role to 'user'
        account.system_role = SystemRole.USER.value

        click.echo(click.style(f"Success! Removed system_admin role from {email}.", fg="green"))
        click.echo(f"  New role: {SystemRole.USER.value}")


# Backward compatibility alias
@click.command("custom-remove-super-admin", help="[CUSTOM] Alias for custom-remove-system-admin (deprecated).")
@click.option("--email", prompt=True, help="Account email to remove system_admin from")
@click.option("--confirm", is_flag=True, help="Confirm the action")
def custom_remove_super_admin(email: str, confirm: bool):
    """Deprecated alias for custom_remove_system_admin."""
    click.echo(click.style(
        "Warning: 'custom-remove-super-admin' is deprecated. Use 'custom-remove-system-admin' instead.",
        fg="yellow"
    ))
    # Invoke the new command's callback directly to bypass Click parsing
    custom_remove_system_admin.callback(email, confirm)
