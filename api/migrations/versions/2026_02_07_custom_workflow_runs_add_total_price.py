"""[CUSTOM] Add custom_total_price and custom_currency to workflow_runs

Adds custom_total_price (Numeric(10,7)) and custom_currency (String(255)) columns
to the workflow_runs table, then backfills custom_total_price from
workflow_node_executions execution_metadata JSON.

Revision ID: custom_workflow_price_001
Revises: custom_system_role_002
Create Date: 2026-02-07
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "custom_workflow_price_001"
down_revision = "custom_system_role_002"
branch_labels = None
depends_on = None


def upgrade():
    """Add custom_total_price and custom_currency columns, then backfill from node executions."""
    with op.batch_alter_table("workflow_runs", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "custom_total_price",
                sa.Numeric(precision=10, scale=7),
                server_default=sa.text("0"),
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column("custom_currency", sa.String(length=255), server_default="USD", nullable=False)
        )

    # Backfill custom_total_price from workflow_node_executions.execution_metadata JSON.
    # Uses MySQL-compatible JOIN syntax (also works on PostgreSQL).
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        op.execute(
            """
            UPDATE workflow_runs wr
            SET custom_total_price = COALESCE(sub.agg_price, 0)
            FROM (
                SELECT workflow_run_id,
                    SUM(COALESCE((execution_metadata::json->>'total_price')::numeric, 0)) AS agg_price
                FROM workflow_node_executions
                WHERE workflow_run_id IS NOT NULL
                    AND execution_metadata IS NOT NULL
                    AND execution_metadata != ''
                GROUP BY workflow_run_id
            ) sub
            WHERE wr.id = sub.workflow_run_id
            """
        )
    else:
        # MySQL / SQLite compatible syntax
        op.execute(
            """
            UPDATE workflow_runs wr
            JOIN (
                SELECT workflow_run_id,
                    SUM(COALESCE(
                        CAST(JSON_UNQUOTE(JSON_EXTRACT(execution_metadata, '$.total_price')) AS DECIMAL(10,7)),
                        0
                    )) AS agg_price
                FROM workflow_node_executions
                WHERE workflow_run_id IS NOT NULL
                    AND execution_metadata IS NOT NULL
                    AND execution_metadata != ''
                GROUP BY workflow_run_id
            ) sub ON wr.id = sub.workflow_run_id
            SET wr.custom_total_price = COALESCE(sub.agg_price, 0)
            """
        )


def downgrade():
    """Remove custom_total_price and custom_currency columns."""
    with op.batch_alter_table("workflow_runs", schema=None) as batch_op:
        batch_op.drop_column("custom_currency")
        batch_op.drop_column("custom_total_price")
