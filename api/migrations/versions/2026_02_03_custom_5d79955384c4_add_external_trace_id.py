"""[CUSTOM] Add external_trace_id to workflow_runs and messages

Revision ID: 5d79955384c4
Revises: 9d77545f524e
Create Date: 2026-02-03

"""
import sqlalchemy as sa
from alembic import op


def _is_pg(conn):
    return conn.dialect.name == "postgresql"


# revision identifiers, used by Alembic.
revision = '5d79955384c4'
down_revision = '9d77545f524e'
branch_labels = None
depends_on = None


def upgrade():
    # Add external_trace_id to workflow_runs table
    with op.batch_alter_table('workflow_runs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('external_trace_id', sa.String(length=128), nullable=True))
        batch_op.create_index(
            'workflow_run_external_trace_id_idx',
            ['tenant_id', 'app_id', 'external_trace_id'],
            unique=False
        )

    # Add external_trace_id to messages table
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.add_column(sa.Column('external_trace_id', sa.String(length=128), nullable=True))
        batch_op.create_index(
            'message_external_trace_id_idx',
            ['app_id', 'external_trace_id'],
            unique=False
        )


def downgrade():
    # Remove external_trace_id from messages table
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.drop_index('message_external_trace_id_idx')
        batch_op.drop_column('external_trace_id')

    # Remove external_trace_id from workflow_runs table
    with op.batch_alter_table('workflow_runs', schema=None) as batch_op:
        batch_op.drop_index('workflow_run_external_trace_id_idx')
        batch_op.drop_column('external_trace_id')
