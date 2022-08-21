"""empty message

Revision ID: 6487cf6f50ac
Revises: affecf1851ce
Create Date: 2022-08-21 20:37:44.345815

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6487cf6f50ac'
down_revision = 'affecf1851ce'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('start_time', sa.DateTime(), nullable=True))
    op.add_column('shows', sa.Column('venue_name', sa.String(), nullable=True))
    op.add_column('shows', sa.Column('artist_name', sa.String(), nullable=True))
    op.add_column('shows', sa.Column('artist_image_link', sa.String(length=500), nullable=True))
    op.drop_column('shows', 'datetime')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('datetime', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('shows', 'artist_image_link')
    op.drop_column('shows', 'artist_name')
    op.drop_column('shows', 'venue_name')
    op.drop_column('shows', 'start_time')
    # ### end Alembic commands ###
