"""merge content automation and cascade delete

Revision ID: c5453241cfab
Revises: 1a31ce608336, a1b2c3d4e5f6
Create Date: 2025-12-25 15:24:16.836167

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'c5453241cfab'
down_revision = ('1a31ce608336', 'a1b2c3d4e5f6')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
