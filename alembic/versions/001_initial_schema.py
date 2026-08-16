"""001_initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-05 14:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create tickets table
    op.create_table(
        'tickets',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('priority', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='OPEN'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create comments table
    op.create_table(
        'comments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('ticket_id', sa.String(length=36), nullable=False),
        sa.Column('author', sa.String(length=255), nullable=False),
        sa.Column('comment_text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comments_ticket_id'), 'comments', ['ticket_id'], unique=False)

    # Create attachments table
    op.create_table(
        'attachments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('ticket_id', sa.String(length=36), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_key', sa.String(length=500), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_attachments_ticket_id'), 'attachments', ['ticket_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_attachments_ticket_id'), table_name='attachments')
    op.drop_table('attachments')
    op.drop_index(op.f('ix_comments_ticket_id'), table_name='comments')
    op.drop_table('comments')
    op.drop_table('tickets')
