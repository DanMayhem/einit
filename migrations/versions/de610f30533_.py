"""empty message

Revision ID: de610f30533
Revises: 3df8c312c845
Create Date: 2014-05-07 12:05:24.265000

"""

# revision identifiers, used by Alembic.
revision = 'de610f30533'
down_revision = '3df8c312c845'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('monster_actions', sa.Column('hash_key', sa.String(length=5), nullable=True))
    op.create_index('ix_monster_actions_hash_key', 'monster_actions', ['hash_key'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_monster_actions_hash_key', table_name='monster_actions')
    op.drop_column('monster_actions', 'hash_key')
    ### end Alembic commands ###
