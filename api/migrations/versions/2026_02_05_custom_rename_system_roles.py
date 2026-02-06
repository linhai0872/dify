"""[CUSTOM] Rename system roles for clarity

Renames system role values in the accounts table:
- super_admin → system_admin
- workspace_admin → tenant_manager
- normal → user

Also adds created_by field to tenants table for tenant_manager permission tracking.

Revision ID: custom_system_role_002
Revises: custom_system_role_001
Create Date: 2026-02-05
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "custom_system_role_002"
down_revision = "custom_system_role_001"
branch_labels = None
depends_on = None


def upgrade():
    """Rename system role values and add created_by to tenants."""
    # Rename system role values in accounts table
    op.execute(
        "UPDATE accounts SET system_role = 'system_admin' WHERE system_role = 'super_admin'"
    )
    op.execute(
        "UPDATE accounts SET system_role = 'tenant_manager' WHERE system_role = 'workspace_admin'"
    )
    op.execute("UPDATE accounts SET system_role = 'user' WHERE system_role = 'normal'")

    # Update server default from 'normal' to 'user'
    with op.batch_alter_table("accounts", schema=None) as batch_op:
        batch_op.alter_column(
            "system_role",
            existing_type=sa.String(length=20),
            server_default="user",
        )

    # Add created_by column to tenants table for tracking workspace creators
    with op.batch_alter_table("tenants", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "created_by",
                sa.String(length=255),
                nullable=True,
            )
        )
        batch_op.create_index(
            "idx_tenants_created_by",
            ["created_by"],
            unique=False,
        )


def downgrade():
    """Revert system role names and remove created_by from tenants."""
    # Remove created_by from tenants
    with op.batch_alter_table("tenants", schema=None) as batch_op:
        batch_op.drop_index("idx_tenants_created_by")
        batch_op.drop_column("created_by")

    # Revert server default
    with op.batch_alter_table("accounts", schema=None) as batch_op:
        batch_op.alter_column(
            "system_role",
            existing_type=sa.String(length=20),
            server_default="normal",
        )

    # Revert system role values
    op.execute(
        "UPDATE accounts SET system_role = 'super_admin' WHERE system_role = 'system_admin'"
    )
    op.execute(
        "UPDATE accounts SET system_role = 'workspace_admin' WHERE system_role = 'tenant_manager'"
    )
    op.execute("UPDATE accounts SET system_role = 'normal' WHERE system_role = 'user'")
