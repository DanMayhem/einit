"""empty message

Revision ID: 25acbb7ff00d
Revises: None
Create Date: 2014-04-01 12:44:05.739000

"""

# revision identifiers, used by Alembic.
revision = '25acbb7ff00d'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_digest', sa.String(length=64), nullable=True),
    sa.Column('session_digest', sa.String(length=64), nullable=True),
    sa.Column('role', sa.SmallInteger(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_name', 'users', ['name'], unique=True)
    op.create_index('ix_users_session_digest', 'users', ['session_digest'], unique=True)
    op.create_table('monsters',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('level', sa.Integer(), nullable=True),
    sa.Column('second_role', sa.String(length=64), nullable=True),
    sa.Column('origin', sa.String(length=64), nullable=True),
    sa.Column('monster_type', sa.String(length=64), nullable=True),
    sa.Column('keywords', sa.String(length=256), nullable=True),
    sa.Column('max_hp', sa.Integer(), nullable=True),
    sa.Column('initiative_modifier', sa.Integer(), nullable=True),
    sa.Column('ac', sa.Integer(), nullable=True),
    sa.Column('fortitude', sa.Integer(), nullable=True),
    sa.Column('reflex', sa.Integer(), nullable=True),
    sa.Column('will', sa.Integer(), nullable=True),
    sa.Column('perception', sa.Integer(), nullable=True),
    sa.Column('senses', sa.String(length=256), nullable=True),
    sa.Column('speed', sa.String(length=64), nullable=True),
    sa.Column('immune', sa.String(length=64), nullable=True),
    sa.Column('resist', sa.String(length=64), nullable=True),
    sa.Column('vulnerable', sa.String(length=64), nullable=True),
    sa.Column('saving_throws', sa.Integer(), nullable=True),
    sa.Column('action_points', sa.Integer(), nullable=True),
    sa.Column('creator_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('heroes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('hero_name', sa.String(length=64), nullable=True),
    sa.Column('player_name', sa.String(length=66), nullable=True),
    sa.Column('level', sa.Integer(), nullable=True),
    sa.Column('max_hp', sa.Integer(), nullable=True),
    sa.Column('initiative_modifier', sa.Integer(), nullable=True),
    sa.Column('creator_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('monster_actions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category', sa.String(length=64), nullable=True),
    sa.Column('usage', sa.String(length=64), nullable=True),
    sa.Column('recharge', sa.Integer(), nullable=True),
    sa.Column('frequency', sa.String(length=64), nullable=True),
    sa.Column('icon', sa.String(length=64), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('description', sa.String(length=512), nullable=True),
    sa.Column('requirement', sa.String(length=64), nullable=True),
    sa.Column('attack', sa.String(length=64), nullable=True),
    sa.Column('hit', sa.String(length=128), nullable=True),
    sa.Column('miss', sa.String(length=128), nullable=True),
    sa.Column('effect', sa.String(length=128), nullable=True),
    sa.Column('secondary_attack', sa.String(length=128), nullable=True),
    sa.Column('aftereffect', sa.String(length=128), nullable=True),
    sa.Column('special', sa.String(length=512), nullable=True),
    sa.Column('keywords', sa.String(length=64), nullable=True),
    sa.Column('monster_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['monster_id'], ['monsters.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('monster_actions')
    op.drop_table('heroes')
    op.drop_table('monsters')
    op.drop_index('ix_users_session_digest', table_name='users')
    op.drop_index('ix_users_name', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
    ### end Alembic commands ###
