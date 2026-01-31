"""add_priority_to_todos

Revision ID: 2b77e7e48cec
Revises: a2b12d33d9e1
Create Date: 2026-01-31 12:33:38.504496

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '2b77e7e48cec'
down_revision: Union[str, Sequence[str], None] = 'a2b12d33d9e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define the enum type
priority_enum = postgresql.ENUM('HIGH', 'MEDIUM', 'LOW', name='priority', create_type=False)


def upgrade() -> None:
    """Upgrade schema."""
    # Create the enum type for PostgreSQL
    priority_enum.create(op.get_bind(), checkfirst=True)
    
    op.add_column('todos', sa.Column('priority', priority_enum, nullable=False, server_default='MEDIUM'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('todos', 'priority')
    
    # Drop the enum type for PostgreSQL
    priority_enum.drop(op.get_bind(), checkfirst=True)
