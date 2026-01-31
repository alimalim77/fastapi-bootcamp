"""add_boards_and_board_members

Revision ID: ae4436b2b87c
Revises: 2b77e7e48cec
Create Date: 2026-01-31 15:28:29.658116

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'ae4436b2b87c'
down_revision: Union[str, Sequence[str], None] = '2b77e7e48cec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define the enum type
boardrole_enum = postgresql.ENUM('ADMIN', 'MEMBER', name='boardrole', create_type=False)


def upgrade() -> None:
    """Upgrade schema."""
    # Create the enum type for PostgreSQL
    boardrole_enum.create(op.get_bind(), checkfirst=True)
    
    op.create_table('boards',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=500), nullable=True),
    sa.Column('color', sa.String(length=7), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_boards_id'), 'boards', ['id'], unique=False)
    op.create_table('board_members',
    sa.Column('board_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('role', boardrole_enum, nullable=False),
    sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['board_id'], ['boards.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('board_id', 'user_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('board_members')
    op.drop_index(op.f('ix_boards_id'), table_name='boards')
    op.drop_table('boards')
    
    # Drop the enum type for PostgreSQL
    boardrole_enum.drop(op.get_bind(), checkfirst=True)
