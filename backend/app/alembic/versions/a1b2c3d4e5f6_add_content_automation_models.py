"""Add content automation models

Revision ID: a1b2c3d4e5f6
Revises: d98dd8ec85a3
Create Date: 2025-12-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'd98dd8ec85a3'
branch_labels = None
depends_on = None


def upgrade():
    # Create socialaccount table
    op.create_table('socialaccount',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('account_name', sa.String(length=255), nullable=False),
        sa.Column('account_handle', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('access_token', sa.String(), nullable=False),
        sa.Column('refresh_token', sa.String(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('owner_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create mediaasset table
    op.create_table('mediaasset',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('media_type', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('alt_text', sa.String(length=500), nullable=True),
        sa.Column('tags', sa.String(length=500), nullable=True),
        sa.Column('storage_url', sa.String(), nullable=False),
        sa.Column('thumbnail_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('owner_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create contenttemplate table
    op.create_table('contenttemplate',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('content_type', sa.String(), nullable=False),
        sa.Column('template_content', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=False),
        sa.Column('usage_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('owner_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create campaign table
    op.create_table('campaign',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('goal', sa.String(length=500), nullable=True),
        sa.Column('target_platforms', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('owner_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create content table
    op.create_table('content',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('content_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('body', sa.String(), nullable=True),
        sa.Column('content_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('owner_id', sa.Uuid(), nullable=False),
        sa.Column('campaign_id', sa.Uuid(), nullable=True),
        sa.Column('template_id', sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaign.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['template_id'], ['contenttemplate.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create contentvariant table
    op.create_table('contentvariant',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('platform_specific_data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('scheduled_for', sa.DateTime(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('platform_post_id', sa.String(length=255), nullable=True),
        sa.Column('platform_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('content_id', sa.Uuid(), nullable=False),
        sa.Column('social_account_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['content_id'], ['content.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['social_account_id'], ['socialaccount.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create contentanalytics table
    op.create_table('contentanalytics',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('metrics', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('fetched_at', sa.DateTime(), nullable=False),
        sa.Column('content_variant_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['content_variant_id'], ['contentvariant.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table('contentanalytics')
    op.drop_table('contentvariant')
    op.drop_table('content')
    op.drop_table('campaign')
    op.drop_table('contenttemplate')
    op.drop_table('mediaasset')
    op.drop_table('socialaccount')
