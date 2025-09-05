"""Create initial tables

Revision ID: a19beb7eb7c5
Revises: 
Create Date: 2025-09-05 20:22:04.205302

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a19beb7eb7c5'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create emails table
    op.create_table('emails',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('sender_email', sa.String(length=255), nullable=False),
        sa.Column('subject', sa.Text(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('received_at', sa.DateTime(), nullable=False),
        sa.Column('sentiment', sa.Enum('POSITIVE', 'NEGATIVE', 'NEUTRAL', name='sentimenttype'), nullable=False),
        sa.Column('priority', sa.Enum('URGENT', 'NOT_URGENT', name='prioritylevel'), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'PROCESSED', 'RESOLVED', 'FAILED', name='emailstatus'), nullable=False),
        sa.Column('extracted_info', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create email_providers table
    op.create_table('email_providers',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('provider_type', sa.Enum('GMAIL', 'OUTLOOK', 'IMAP', name='providertype'), nullable=False),
        sa.Column('configuration', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create responses table
    op.create_table('responses',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email_id', sa.String(), nullable=False),
        sa.Column('generated_content', sa.Text(), nullable=False),
        sa.Column('edited_content', sa.Text(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'SENT', 'FAILED', name='responsestatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['email_id'], ['emails.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create knowledge_items table
    op.create_table('knowledge_items',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order
    op.drop_table('knowledge_items')
    op.drop_table('responses')
    op.drop_table('email_providers')
    op.drop_table('emails')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS responsestatus")
    op.execute("DROP TYPE IF EXISTS providertype")
    op.execute("DROP TYPE IF EXISTS emailstatus")
    op.execute("DROP TYPE IF EXISTS prioritylevel")
    op.execute("DROP TYPE IF EXISTS sentimenttype")
