#!python
import Crypto.Random
import hashlib
import sqlalchemy
import sqlalchemy.orm

import einit

_db = einit.db

class UserModel(_db.Model):
  __tablename__ = 'users'
  id = _db.Column(_db.Integer, primary_key = True)
  name = _db.Column(_db.String(64), index = True, unique = True)
  email = _db.Column(_db.String(120), index = True, unique = True)
  password_digest = _db.Column(_db.String(64))
  session_digest = _db.Column(_db.String(64), index = True, unique = True)
  role = _db.Column(_db.SmallInteger, default = 0)

  heroes = sqlalchemy.orm.relationship("HeroModel")
  monsters = sqlalchemy.orm.relationship("MonsterModel")
  encounters = sqlalchemy.orm.relationship("EncounterModel")

  def __init__(self, name, email, password):
    self.name = name
    self.email = email.lower()
    self.password_digest = einit.bcrypt.generate_password_hash(password)
    sha = hashlib.sha1()
    sha.update(Crypto.Random.get_random_bytes(32))
    self.session_digest = hashlib.sha1(Crypto.Random.get_random_bytes(32)).hexdigest()

  def __repr__(self):
    return '<UserModel %r>' % (self.name)

class HeroModel(_db.Model):
  __tablename__='heroes'
  id = _db.Column(_db.Integer, primary_key = True)
  hero_name = _db.Column(_db.String(64))
  player_name = _db.Column(_db.String(66))
  level = _db.Column(_db.Integer)
  max_hp = _db.Column(_db.Integer)
  initiative_modifier = _db.Column(_db.Integer)

  creator_id = _db.Column(_db.Integer,_db.ForeignKey('users.id'))

class MonsterModel(_db.Model):
  __tablename__='monsters'
  id = _db.Column(_db.Integer, primary_key = True)
  name = _db.Column(_db.String(64))
  level = _db.Column(_db.Integer)
  second_role = _db.Column(_db.String(64))
  origin = _db.Column(_db.String(64))
  monster_type = _db.Column(_db.String(64))
  keywords = _db.Column(_db.String(256))
  max_hp = _db.Column(_db.Integer)
  initiative_modifier = _db.Column(_db.Integer)
  ac = _db.Column(_db.Integer)
  fortitude = _db.Column(_db.Integer)
  reflex = _db.Column(_db.Integer)
  will = _db.Column(_db.Integer)
  perception = _db.Column(_db.Integer)
  senses = _db.Column(_db.String(256))
  speed = _db.Column(_db.String(64))
  immune = _db.Column(_db.String(64))
  resist = _db.Column(_db.String(64))
  vulnerable = _db.Column(_db.String(64))
  saving_throws = _db.Column(_db.Integer)
  action_points = _db.Column(_db.Integer)
  actions = sqlalchemy.orm.relationship("MonsterActionModel")

  creator_id = _db.Column(_db.Integer,_db.ForeignKey('users.id'))

class MonsterActionModel(_db.Model):
  __tablename__ = 'monster_actions'
  id = _db.Column(_db.Integer, primary_key = True)
  category = _db.Column(_db.String(64))
  aura_range = _db.Column(_db.String(64))
  recharge = _db.Column(_db.String(64))
  frequency = _db.Column(_db.String(64))
  icon = _db.Column(_db.String(64))
  name = _db.Column(_db.String(64))
  description = _db.Column(_db.String(512))
  trigger = _db.Column(_db.String(512))
  trigger_usage = _db.Column(_db.String(512))
  attack = _db.Column(_db.String(64))
  hit = _db.Column(_db.String(512))
  miss = _db.Column(_db.String(512))
  effect = _db.Column(_db.String(512))
  secondary_attack = _db.Column(_db.String(512))
  aftereffect = _db.Column(_db.String(512))
  special = _db.Column(_db.String(512))
  keywords = _db.Column(_db.String(64))

  monster_id = _db.Column(_db.Integer,_db.ForeignKey('monsters.id'))

class EncounterModel(_db.Model):
  __tablename__ = 'encounters'
  id = _db.Column(_db.Integer, primary_key = True)
  name = _db.Column(_db.String(64))
  description = _db.Column(_db.String(512))
  round = _db.Column(_db.Integer, default=0)
  current_entry = _db.Column(_db.Integer)
  actors = sqlalchemy.orm.relationship("ActorModel")
  events = sqlalchemy.orm.relationship("EventModel")
  entries = sqlalchemy.orm.relationship("EncounterEntryModel", backref="encounter")

  creator_id = _db.Column(_db.Integer,_db.ForeignKey('users.id'))

class ActorModel(_db.Model):
  __tablename__ = 'actors'
  id = _db.Column(_db.Integer, primary_key = True)
  category = _db.Column(_db.String(64))
  reference_id = _db.Column(_db.Integer)
  spawn_count = _db.Column(_db.Integer)
  initiative = _db.Column(_db.Integer)

  encounter_id = _db.Column(_db.Integer,_db.ForeignKey('encounters.id'))

class EventModel(_db.Model):
  __tablename__ = 'encounter_events'
  id = _db.Column(_db.Integer, primary_key = True)
  name = _db.Column(_db.String(64))
  description = _db.Column(_db.String(512))

  encounter_id = _db.Column(_db.Integer,_db.ForeignKey('encounters.id'))


class EncounterEntryModel(_db.Model):
  __tablename__="encounter_entries"
  id = _db.Column(_db.Integer, primary_key = True)
  initiative = _db.Column(_db.Integer)
  initiative_order = _db.Column(_db.Integer)
  spawn_index = _db.Column(_db.Integer)

  hp = _db.Column(_db.Integer)
  temp_hp = _db.Column(_db.Integer)
  visible = _db.Column(_db.SmallInteger, default=1)
  statuses = sqlalchemy.orm.relationship("EncounterEntryStatusModel")

  category = _db.Column(_db.String(64))
  reference_id = _db.Column(_db.Integer)

  encounter_id = _db.Column(_db.Integer,_db.ForeignKey('encounters.id'))

class EncounterEntryStatusModel(_db.Model):
  __tablename__="encounter_entry_statuses"
  id = _db.Column(_db.Integer, primary_key=True)
  status = _db.Column(_db.String(64))

  encounter_entry_id = _db.Column(_db.Integer,_db.ForeignKey('encounter_entries.id'))

