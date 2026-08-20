"""Add guidance engine tables

Revision ID: 002_add_guidance_tables
Revises: 001_initial
Create Date: 2026-08-19 22:40:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid

# revision identifiers, used by Alembic.
revision = '002_add_guidance_tables'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def get_uuid():
    return str(uuid.uuid4())


def upgrade():
    # Create phases table
    op.create_table('phases',
        sa.Column('id', sa.String(), primary_key=True, default=get_uuid),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False, unique=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_phases_order', 'phases', ['order'])

    # Create checklists table
    op.create_table('checklists',
        sa.Column('id', sa.String(), primary_key=True, default=get_uuid),
        sa.Column('phase_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('is_required', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['phase_id'], ['phases.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_checklists_phase_id', 'checklists', ['phase_id'])
    op.create_index('ix_checklists_order', 'checklists', ['order'])

    # Create checklist_items table
    op.create_table('checklist_items',
        sa.Column('id', sa.String(), primary_key=True, default=get_uuid),
        sa.Column('checklist_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('is_required', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['checklist_id'], ['checklists.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_checklist_items_checklist_id', 'checklist_items', ['checklist_id'])
    op.create_index('ix_checklist_items_order', 'checklist_items', ['order'])

    # Create milestones table
    op.create_table('milestones',
        sa.Column('id', sa.String(), primary_key=True, default=get_uuid),
        sa.Column('phase_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('criteria', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['phase_id'], ['phases.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_milestones_phase_id', 'milestones', ['phase_id'])
    op.create_index('ix_milestones_order', 'milestones', ['order'])

    # Create user_progress table
    op.create_table('user_progress',
        sa.Column('id', sa.String(), primary_key=True, default=get_uuid),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('checklist_item_id', sa.String(), nullable=False),
        sa.Column('phase_id', sa.String(), nullable=False),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['contacts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['checklist_item_id'], ['checklist_items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['phase_id'], ['phases.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_user_progress_user_id', 'user_progress', ['user_id'])
    op.create_index('ix_user_progress_checklist_item_id', 'user_progress', ['checklist_item_id'])
    op.create_index('ix_user_progress_phase_id', 'user_progress', ['phase_id'])
    # Unique constraint to prevent duplicate progress entries
    op.create_unique_constraint('uq_user_progress_user_item', 'user_progress', ['user_id', 'checklist_item_id'])


def downgrade():
    op.drop_table('user_progress')
    op.drop_table('milestones')
    op.drop_table('checklist_items')
    op.drop_table('checklists')
    op.drop_table('phases')