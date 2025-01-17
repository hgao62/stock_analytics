"""add LastUpdated to  TickerInfo

Revision ID: 052ba12646a1
Revises: cffae460f8dc
Create Date: 2025-01-11 11:17:09.910861

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '052ba12646a1'
down_revision = 'cffae460f8dc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('TickerInfo', sa.Column('LastUpdated', sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('TickerInfo', 'LastUpdated')
    # ### end Alembic commands ###
