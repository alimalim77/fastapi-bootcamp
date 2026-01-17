"""Add role to users

Revision ID: 4ee80663e525
Revises: 8046e178f85d
Create Date: 2026-01-17 12:20:21.252730

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ee80663e525'
down_revision: Union[str, Sequence[str], None] = '8046e178f85d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('role', sa.String(), nullable=True, server_default='user'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'role')
