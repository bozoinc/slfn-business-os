"""Initial migration - create core tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-07-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def get_uuid():
    return str(uuid.uuid4())


def upgrade():
    # Create tags table
    op.create_table('tags',
        sa.Column('id', sa.String(), primary_key=True, default=get_uuid),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('color', sa.String(), nullable=False, server_default='#3b82f6'),
    )

    # Create contacts table
    op.create_table('contacts',
        sa.Column('id', sa.String(), primary_key=True, default=get_uuid),
        sa.Column('first_name', sa.String(), nullable=True),
        sa.Column('last_name', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('company', sa.String(), nullable=True),
        sa.Column('job_title', sa.String(), nullable=True),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('city', sa.String(), nullable=True),
        sa.Column('state', sa.String(), nullable=True),
        sa.Column('zip_code', sa.String(), nullable=True),
        sa.Column('country', sa.String(), nullable=True),
        sa.Column('custom_fields', sa.JSON(), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
    )
    op.create_index('ix_contacts_email', 'contacts', ['email'])
    op.create_index('ix_contacts_first_name', 'contacts', ['first_name'])
    op.create_index('ix_contacts_last_name', 'contacts', ['last_name'])

    # Create contact_tags association table
    op.create_table('contact_tags',
        sa.Column('contact_id', sa.String(), primary_key=True),
        sa.Column('tag_id', sa.String(), primary_key=True),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
    )

    # Create pipelines table
    op.create_table('pipelines',
        sa.Column('id', sa.String(), primary_key=True, default=get_uuid),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('organization_id', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Create stages table
    op.create_table('stages',
        sa.Column('id', sa.String(), primary_key=True, default=get_uuid),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('probability', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('pipeline_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['pipeline_id'], ['pipelines.id'], ondelete='CASCADE'),
    )

    # Create deals table
    op.create_table('deals',
        sa.Column('id', sa.String(), primary_key=True, default=get_uuid),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('value', sa.Integer(), nullable=True),
        sa.Column('stage_id', sa.String(), nullable=True),
        sa.Column('pipeline_id', sa.String(), nullable=False),
        sa.Column('contact_id', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('probability', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.Column('is_won', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['stage_id'], ['stages.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['pipeline_id'], ['pipelines.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='SET NULL'),
    )

    # Create forms table
    op.create_table('forms',
        sa.Column('id', sa.String(), primary_key=True, default=get_uuid),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('fields', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('settings', sa.JSON(), nullable=True, server_default='{}'),
        sa.Column('embed_code', sa.String(), nullable=True),
        sa.Column('submissions_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    # Create form_submissions table
    op.create_table('form_submissions',
        sa.Column('id', sa.String(), primary_key=True, default=get_uuid),
        sa.Column('form_id', sa.String(), nullable=False),
        sa.Column('contact_id', sa.String(), nullable=True),
        sa.Column('data', sa.JSON(), nullable=False),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['form_id'], ['forms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='SET NULL'),
    )


def downgrade():
    op.drop_table('form_submissions')
    op.drop_table('forms')
    op.drop_table('deals')
    op.drop_table('stages')
    op.drop_table('pipelines')
    op.drop_table('contact_tags')
    op.drop_table('contacts')
    op.drop_table('tags')