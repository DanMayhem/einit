#!python
import hashlib

import sqlalchemy.orm
import flask.ext.login

import einit
import db
import actors
import encounters

_db = db._db

class User(flask.ext.login.UserMixin):
  def __init__(self):
    self.u = None

  def get_id(self):
    return self.u.id

  def __repr__(self):
    return '<User %r>' %self.u.name

  def save(self):
    _db.session.add(self.u)
    _db.session.commit()

  def get_gravatar_hash(self):
    return hashlib.md5(self.u.email.lower()).hexdigest()

  def get_name(self):
    return self.u.name

  def check_password(self, password):
    return einit.bcrypt.check_password_hash(self.u.password_digest,password)

  def get_heroes(self):
    return sorted(map(lambda h: einit.models.actors.Hero(self, h), self.u.heroes),key=lambda h:h.hero_name)

  def get_hero_count(self):
    return len(self.u.heroes)  

  def get_hero_by_id(self, hero_id):
    try:
      hero = _db.session.query(db.HeroModel).join(db.UserModel).filter(db.UserModel.id == self.u.id).filter(db.HeroModel.id == hero_id).one()
      return actors.Hero(self, hero)
    except sqlalchemy.orm.exc.NoResultFound:
      return None
    except sqlalchemy.orm.exc.MultipleResultsFound:
      return None

  def get_monsters(self):
    return map(lambda m: actors.Monster(self, m), self.u.monsters)

  def get_monster_count(self):
    return len(self.u.monsters)  

  def get_monster_by_id(self, monster_id):
    try:
      monster = _db.session.query(db.MonsterModel).join(db.UserModel).filter(db.UserModel.id == self.u.id).filter(db.MonsterModel.id == monster_id).one()
      return actors.Monster(self, monster)
    except sqlalchemy.orm.exc.NoResultFound:
      return None
    except sqlalchemy.orm.exc.MultipleResultsFound:
      return None

  def get_encounters(self):
    return sorted(map(lambda e: encounters.Encounter(self, e), self.u.encounters), key=lambda x: x.name)

  def get_encounter_count(self):
    return len(self.u.encounters)  

  def get_encounter_by_id(self, encounter_id):
    try:
      encounter = _db.session.query(db.EncounterModel).join(db.UserModel).filter(db.UserModel.id == self.u.id).filter(db.EncounterModel.id == encounter_id).one()
      return einit.models.encounters.Encounter(self, encounter)
    except sqlalchemy.orm.exc.NoResultFound:
      return None
    except sqlalchemy.orm.exc.MultipleResultsFound:
      return None

  @staticmethod
  def get_user_by_name(name):
    try:
      u = User()
      u.u = _db.session.query(db.UserModel).filter(db.UserModel.name == name).one()
      return u
    except sqlalchemy.orm.exc.NoResultFound:
      return None
    except sqlalchemy.orm.exc.MultipleResultsFound:
      return None

  @staticmethod
  def get_user_by_email(email):
    try:
      u = User()
      u.u = _db.session.query(db.UserModel).filter(db.UserModel.email == email).one()
      return u
    except sqlalchemy.orm.exc.NoResultFound:
      return None
    except sqlalchemy.orm.exc.MultipleResultsFound:
      return None

  @staticmethod
  def does_username_exist(name):
    return User.get_user_by_name(name) is not None
    
  @staticmethod
  def does_email_exist(email):
    return User.get_user_by_email(email) is not None
  
  @staticmethod
  def get_user_by_id(id):
    if id == 'None':
      return None
    try:
      u = User()
      u.u = _db.session.query(db.UserModel).filter(db.UserModel.id == id).one()
      return u
    except sqlalchemy.orm.exc.NoResultFound:
      return None
    except sqlalchemy.orm.exc.MultipleResultsFound:
      return None

  @staticmethod
  def create_user(name, email, password):
    u = User()
    u.u = db.UserModel(name, email, password)
    return u

class AnonymousUser(User):
  def __init__(self):
    self.u = None

  def __repr__(self):
    return "AnonymousUser"

  def save(self):
    pass #maybe raise an exception?

  def get_gravatar_hash(self):
    return 'd41d8cd98f00b204e9800998ecf8427e' #this the md5 of an empy string

  def is_active(self):
    return False

  def is_authenticated(self):
    return False

  def is_anonymous(self):
    return True

  def get_id(self):
    return None

  def get_name(self):
    return 'Anonymous'


@einit.login_manager.user_loader
def load_user(userid):
  return User.get_user_by_id(userid)
