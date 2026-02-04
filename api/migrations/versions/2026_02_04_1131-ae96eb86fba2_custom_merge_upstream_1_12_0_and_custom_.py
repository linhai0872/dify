"""[CUSTOM] merge upstream 1.12.0 and custom migrations

Revision ID: ae96eb86fba2
Revises: 788d3099ae3a, 5d79955384c4
Create Date: 2026-02-04 11:31:14.042011

"""
from alembic import op
import models as models
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ae96eb86fba2'
down_revision = ('788d3099ae3a', '5d79955384c4')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
