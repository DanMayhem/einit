"""empty message

Revision ID: 4bf70bd6351c
Revises: dc1a7ceb7cf
Create Date: 2014-04-10 12:51:02.743000

"""

# revision identifiers, used by Alembic.
revision = '4bf70bd6351c'
down_revision = 'dc1a7ceb7cf'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('encounter_events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('description', sa.String(length=512), nullable=True),
    sa.Column('encounter_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['encounter_id'], ['encounters.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('encounter_events')
    ### end Alembic commands ###
