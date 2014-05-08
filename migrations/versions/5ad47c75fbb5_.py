"""empty message

Revision ID: 5ad47c75fbb5
Revises: 8caeebb643a
Create Date: 2014-04-22 14:44:58.774000

"""

# revision identifiers, used by Alembic.
revision = '5ad47c75fbb5'
down_revision = '8caeebb643a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('encounters', sa.Column('current_entry', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('encounters', 'current_entry')
    ### end Alembic commands ###