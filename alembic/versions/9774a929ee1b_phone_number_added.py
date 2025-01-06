"""phone_number added

Revision ID: 9774a929ee1b
Revises: 
Create Date: 2025-01-05 18:54:02.089453

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9774a929ee1b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number', sa.String, nullable=True))


def downgrade() -> None:
    # op.drop_column('users', 'phone_number')
    pass
