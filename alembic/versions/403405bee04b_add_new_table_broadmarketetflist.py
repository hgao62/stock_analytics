"""add new table BroadMarketETFList

Revision ID: 403405bee04b
Revises: 876ea8453f7a
Create Date: 2025-01-08 13:30:46.696333

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '403405bee04b'
down_revision = '876ea8453f7a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Broad_Market_ETFs',
    sa.Column('Ticker', sa.String(), nullable=False),
    sa.Column('Name', sa.String(), nullable=True),
    sa.Column('Sector', sa.String(), nullable=True),
    sa.Column('Asset_Class', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('Ticker')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Broad_Market_ETFs')
    # ### end Alembic commands ###
