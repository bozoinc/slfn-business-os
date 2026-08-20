"""Add documents table for PDF intake pipeline

Revision ID: 003_add_documents_table
Revises: 002_add_guidance_tables
Create Date: 2026-08-20 06:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid

# revision identifiers, used by Alembic.
revision = '003_add_documents_table'
down_revision = '002_add_guidance_tables'
branch_labels = None
depends_on = None


def get_uuid():
    return str(uuid.uuid4())


def upgrade():
    # Create documents table
    op.create_table('documents',
        sa.Column('id', sa.String(), primary_key=True, default=get_uuid),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('original_filename', sa.String(), nullable=False),
        sa.Column('content_type', sa.String(), nullable=False, server_default='application/pdf'),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('minio_object_name', sa.String(), nullable=True),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('extracted_metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('uploaded_by', sa.String(), nullable=True),
        sa.Column('phase_id', sa.String(), nullable=True),
        sa.Column('checklist_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['uploaded_by'], ['contacts.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['phase_id'], ['phases.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['checklist_id'], ['checklists.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_documents_uploaded_by', 'documents', ['uploaded_by'])
    op.create_index('ix_documents_phase_id', 'documents', ['phase_id'])
    op.create_index('ix_documents_checklist_id', 'documents', ['checklist_id'])
    op.create_index('ix_documents_status', 'documents', ['status'])
    op.create_index('ix_documents_created_at', 'documents', ['created_at'])


def downgrade():
    op.drop_table('documents')