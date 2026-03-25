"""[CUSTOM] Rename external_trace_id to custom_external_trace_id

Rename the external_trace_id columns in workflow_runs and messages tables
to comply with the custom field naming convention (custom_ prefix required
for fields added to upstream tables).

Revision ID: custom_rename_external_trace_id
Revises: dfff1a14ed50
Create Date: 2026-03-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'custom_rename_external_trace_id'
down_revision = 'dfff1a14ed50'
branch_labels = None
depends_on = None


def upgrade():
    # Rename external_trace_id → custom_external_trace_id in workflow_runs
    with op.batch_alter_table('workflow_runs', schema=None) as batch_op:
        batch_op.drop_index('workflow_run_external_trace_id_idx')
        batch_op.alter_column(
            'external_trace_id',
            new_column_name='custom_external_trace_id',
            existing_type=sa.String(length=128),
            existing_nullable=True,
        )
        batch_op.create_index(
            'workflow_run_custom_external_trace_id_idx',
            ['tenant_id', 'app_id', 'custom_external_trace_id'],
            unique=False,
        )

    # Rename external_trace_id → custom_external_trace_id in messages
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.drop_index('message_external_trace_id_idx')
        batch_op.alter_column(
            'external_trace_id',
            new_column_name='custom_external_trace_id',
            existing_type=sa.String(length=128),
            existing_nullable=True,
        )
        batch_op.create_index(
            'message_custom_external_trace_id_idx',
            ['app_id', 'custom_external_trace_id'],
            unique=False,
        )


def downgrade():
    # Reverse: messages
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.drop_index('message_custom_external_trace_id_idx')
        batch_op.alter_column(
            'custom_external_trace_id',
            new_column_name='external_trace_id',
            existing_type=sa.String(length=128),
            existing_nullable=True,
        )
        batch_op.create_index(
            'message_external_trace_id_idx',
            ['app_id', 'external_trace_id'],
            unique=False,
        )

    # Reverse: workflow_runs
    with op.batch_alter_table('workflow_runs', schema=None) as batch_op:
        batch_op.drop_index('workflow_run_custom_external_trace_id_idx')
        batch_op.alter_column(
            'custom_external_trace_id',
            new_column_name='external_trace_id',
            existing_type=sa.String(length=128),
            existing_nullable=True,
        )
        batch_op.create_index(
            'workflow_run_external_trace_id_idx',
            ['tenant_id', 'app_id', 'external_trace_id'],
            unique=False,
        )
