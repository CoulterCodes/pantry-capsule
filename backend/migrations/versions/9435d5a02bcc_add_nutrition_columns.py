"""add nutrition columns

Revision ID: 9435d5a02bcc
Revises: 01317beee1c2
Create Date: 2025-11-16 06:38:03.990621

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9435d5a02bcc'
down_revision: Union[str, Sequence[str], None] = '01317beee1c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
