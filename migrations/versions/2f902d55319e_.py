"""empty message

Revision ID: 2f902d55319e
Revises: 15f74d07f5db
Create Date: 2014-04-03 10:30:07.667000

"""

# revision identifiers, used by Alembic.
revision = '2f902d55319e'
down_revision = '15f74d07f5db'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('monster_actions', sa.Column('trigger', sa.String(length=64), nullable=True))
    op.drop_column('monster_actions', 'requirement')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('monster_actions', sa.Column('requirement', sa.VARCHAR(length=64), nullable=True))
    op.drop_column('monster_actions', 'trigger')
    ### end Alembic commands ###
