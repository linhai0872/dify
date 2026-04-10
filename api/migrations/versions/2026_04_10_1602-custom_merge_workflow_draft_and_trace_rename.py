"""Merge heads: upstream workflow_draft_variables + custom external_trace rename

Revision ID: custom_merge_workflow_draft_and_trace_rename
Revises: 6b5f9f8b1a2c, custom_rename_external_trace_id
Create Date: 2026-04-10 16:02:00.456084

"""
# revision identifiers, used by Alembic.
revision = "custom_merge_workflow_draft_and_trace_rename"
down_revision = ("6b5f9f8b1a2c", "custom_rename_external_trace_id")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
