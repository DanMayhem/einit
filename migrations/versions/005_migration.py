from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
monster_actions = Table('monster_actions', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('category', String(length=64)),
    Column('usage', String(length=64)),
    Column('recharge', String(length=64)),
    Column('frequency', String(length=64)),
    Column('icon', String(length=64)),
    Column('name', String(length=64)),
    Column('description', String(length=512)),
    Column('requirement', String(length=64)),
    Column('attack', String(length=64)),
    Column('hit', String(length=128)),
    Column('miss', String(length=128)),
    Column('effect', String(length=128)),
    Column('secondary_attack', String(length=128)),
    Column('aftereffect', String(length=128)),
    Column('special', String(length=512)),
    Column('monster_id', Integer),
)

monsters = Table('monsters', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=64)),
    Column('level', Integer),
    Column('second_role', String(length=64)),
    Column('origin', String(length=64)),
    Column('monster_type', String(length=64)),
    Column('keywords', String(length=256)),
    Column('max_hp', Integer),
    Column('initiative_modifier', Integer),
    Column('ac', Integer),
    Column('fortitude', Integer),
    Column('reflex', Integer),
    Column('will', Integer),
    Column('perception', Integer),
    Column('senses', String(length=256)),
    Column('speed', String(length=64)),
    Column('immune', String(length=64)),
    Column('resist', String(length=64)),
    Column('vulnerable', String(length=64)),
    Column('saving_throws', Integer),
    Column('action_points', Integer),
    Column('creator_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['monster_actions'].create()
    post_meta.tables['monsters'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['monster_actions'].drop()
    post_meta.tables['monsters'].drop()
