"""[CUSTOM] Add system_role to accounts table

Adds a system_role field to the accounts table for multi-workspace permission control.
This field stores the system-level role (super_admin/workspace_admin/normal) which is
independent of workspace-level roles (owner/admin/editor/normal/dataset_operator).

Revision ID: custom_system_role_001
Revises: ae96eb86fba2
Create Date: 2026-02-04
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "custom_system_role_001"
down_revision = "ae96eb86fba2"
branch_labels = None
depends_on = None


def upgrade():
    """Add system_role column to accounts table with default value 'normal'."""
    with op.batch_alter_table("accounts", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "system_role",
                sa.String(length=20),
                nullable=False,
                server_default="normal",
            )
        )
        # Add index for efficient filtering by system_role
        batch_op.create_index(
            "idx_accounts_system_role",
            ["system_role"],
            unique=False,
        )


def downgrade():
    """Remove system_role column from accounts table."""
    with op.batch_alter_table("accounts", schema=None) as batch_op:
        batch_op.drop_index("idx_accounts_system_role")
        batch_op.drop_column("system_role")
