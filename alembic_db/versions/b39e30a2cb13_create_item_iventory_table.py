"""create item_iventory table

Revision ID: b39e30a2cb13
Revises: 
Create Date: 2025-07-15 19:44:44.677200

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b39e30a2cb13'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    #"""Upgrade schema."""
    op.create_table('items_iventory',
                    sa.Column('item_id', sa.Integer(), nullable=False, primary_key=True),
                    sa.Column('item_name', sa.String(), nullable=False),
                    sa.Column('item_quantity', sa.Integer(), nullable=False),
                    sa.Column('item_price', sa.Integer(), nullable=False))
    pass


def downgrade() -> None:
    #"""Downgrade schema."""
    op.drop_table('items_iventory')
    pass
