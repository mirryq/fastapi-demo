"""add content column to posts table

Revision ID: a65b814527bb
Revises: 9afcb9b72e5e
Create Date: 2026-09-12 22:06:26.272988

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a65b814527bb'
down_revision: Union[str, Sequence[str], None] = '9afcb9b72e5e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('posts', 'content')
    pass
