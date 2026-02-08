"""add ab testing tables

Revision ID: f8b7d6e5a4c3
Revises: c5453241cfab
Create Date: 2026-02-08 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f8b7d6e5a4c3'
down_revision = 'c5453241cfab'
branch_labels = None
depends_on = None


def upgrade():
    # Create ABTest table
    op.create_table(
        'abtest',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('goal', sa.String(length=50), nullable=False),  # ABTestGoal enum
        sa.Column('confidence_level', sa.Float(), nullable=False, server_default='0.95'),
        sa.Column('min_sample_size', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='draft'),  # ABTestStatus enum
        sa.Column('winner_variant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_abtest_owner_id', 'abtest', ['owner_id'])
    op.create_index('ix_abtest_status', 'abtest', ['status'])

    # Create ABTestVariant table
    op.create_table(
        'abtestvariant',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('ab_test_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content_variant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('variant_name', sa.String(length=100), nullable=False),
        sa.Column('traffic_allocation', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['ab_test_id'], ['abtest.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['content_variant_id'], ['contentvariant.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_abtestvariant_ab_test_id', 'abtestvariant', ['ab_test_id'])
    op.create_index('ix_abtestvariant_content_variant_id', 'abtestvariant', ['content_variant_id'])

    # Create ABTestResult table
    op.create_table(
        'abtestresult',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('ab_test_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('variant_a_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('variant_b_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('variant_a_views', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('variant_a_engagement', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('variant_b_views', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('variant_b_engagement', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('p_value', sa.Float(), nullable=True),
        sa.Column('statistical_significance', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('effect_size', sa.Float(), nullable=True),
        sa.Column('confidence_interval_lower', sa.Float(), nullable=True),
        sa.Column('confidence_interval_upper', sa.Float(), nullable=True),
        sa.Column('calculated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['ab_test_id'], ['abtest.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_abtestresult_ab_test_id', 'abtestresult', ['ab_test_id'])


def downgrade():
    # Drop tables in reverse order
    op.drop_index('ix_abtestresult_ab_test_id', table_name='abtestresult')
    op.drop_table('abtestresult')

    op.drop_index('ix_abtestvariant_content_variant_id', table_name='abtestvariant')
    op.drop_index('ix_abtestvariant_ab_test_id', table_name='abtestvariant')
    op.drop_table('abtestvariant')

    op.drop_index('ix_abtest_status', table_name='abtest')
    op.drop_index('ix_abtest_owner_id', table_name='abtest')
    op.drop_table('abtest')
