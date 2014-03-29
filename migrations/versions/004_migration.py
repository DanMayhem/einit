from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
heroes = Table('heroes', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('hero_name', String(length=64)),
    Column('player_name', String(length=66)),
    Column('level', Integer),
    Column('max_hp', Integer),
    Column('initiative_modifier', Integer),
    Column('creator_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['heroes'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['heroes'].drop()
