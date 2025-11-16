"""Add nutrition summary to MealPlan

Revision ID: 91c129fac9b1
Revises: 9435d5a02bcc
Create Date: 2025-11-16 07:03:26.823853

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '91c129fac9b1'
down_revision: Union[str, Sequence[str], None] = '9435d5a02bcc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
