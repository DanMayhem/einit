import einit
import Crypto.Random
import hashlib
import sqlalchemy
import sqlalchemy.orm

import flask.ext.login

my_db = einit.db

class UserModel(my_db.Model):
  __tablename__ = 'users'
  id = my_db.Column(my_db.Integer, primary_key = True)
  name = my_db.Column(my_db.String(64), index = True, unique = True)
  email = my_db.Column(my_db.String(120), index = True, unique = True)
  password_digest = my_db.Column(my_db.String(64))
  session_digest = my_db.Column(my_db.String(64), index = True, unique = True)
  role = my_db.Column(my_db.SmallInteger, default = 0)

  heroes = sqlalchemy.orm.relationship("HeroModel")

  def __init__(self, name, email, password):
    self.name = name
    self.email = email.lower()
    self.password_digest = einit.bcrypt.generate_password_hash(password)
    sha = hashlib.sha1()
    sha.update(Crypto.Random.get_random_bytes(32))
    self.session_digest = hashlib.sha1(Crypto.Random.get_random_bytes(32)).hexdigest()

  def __repr__(self):
    return '<UserModel %r>' % (self.name)

class User(flask.ext.login.UserMixin):
  def __init__(self):
    self.u = None

  def get_id(self):
    return self.u.id

  def __repr__(self):
    return '<User %r>' %self.u.name

  def save(self):
    my_db.session.add(self.u)
    my_db.session.commit()

  def get_gravatar_hash(self):
    return hashlib.md5(self.u.email.lower()).hexdigest()

  def get_name(self):
    return self.u.name

  def check_password(self, password):
    return einit.bcrypt.check_password_hash(self.u.password_digest,password)

  def get_heroes(self):
    return map(lambda h: Hero(self, h), self.u.heroes)

  def get_hero_count(self):
    return len(self.u.heroes)  

  def get_hero_by_id(self, hero_id):
    try:
      hero = my_db.session.query(HeroModel).join(UserModel).filter(UserModel.id == self.u.id).filter(HeroModel.id == hero_id).one()
      return Hero(self, hero)
    except sqlalchemy.orm.exc.NoResultFound:
      return None
    except sqlalchemy.orm.exc.MultipleResultsFound:
      return None

  @staticmethod
  def get_user_by_name(name):
    try:
      u = User()
      u.u = my_db.session.query(UserModel).filter(UserModel.name == name).one()
      return u
    except sqlalchemy.orm.exc.NoResultFound:
      return None
    except sqlalchemy.orm.exc.MultipleResultsFound:
      return None

  @staticmethod
  def get_user_by_email(email):
    try:
      u = User()
      u.u = my_db.session.query(UserModel).filter(UserModel.email == email).one()
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
      u.u = my_db.session.query(UserModel).filter(UserModel.id == id).one()
      return u
    except sqlalchemy.orm.exc.NoResultFound:
      return None
    except sqlalchemy.orm.exc.MultipleResultsFound:
      return None

  @staticmethod
  def create_user(name, email, password):
    u = User()
    u.u = UserModel(name, email, password)
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

class HeroModel(my_db.Model):
  __tablename__='heroes'
  id = my_db.Column(my_db.Integer, primary_key = True)
  hero_name = my_db.Column(my_db.String(64))
  player_name = my_db.Column(my_db.String(66))
  level = my_db.Column(my_db.Integer)
  max_hp = my_db.Column(my_db.Integer)
  initiative_modifier = my_db.Column(my_db.Integer)

  creator_id = my_db.Column(my_db.Integer,my_db.ForeignKey('users.id'))

class Hero(object):
  def __init__(self, u, hm=None):
    if hm is None:
      self.hero_model = HeroModel()
      self.hero_model.creator_id = u.get_id()
    else:
      self.hero_model = hm

  @property
  def hero_name(self):
    return self.hero_model.hero_name
  @hero_name.setter
  def hero_name(self, value):
    self.hero_model.hero_name = value

  @property
  def player_name(self):
    return self.hero_model.player_name
  @player_name.setter
  def player_name(self, value):
    self.hero_model.player_name = value

  @property
  def level(self):
    return self.hero_model.level
  @level.setter
  def level(self, value):
    self.hero_model.level = value

  @property
  def max_hp(self):
    return self.hero_model.max_hp
  @max_hp.setter
  def max_hp(self, value):
    self.hero_model.max_hp = value

  @property
  def initiative_modifier(self):
    return self.hero_model.initiative_modifier
  @initiative_modifier.setter
  def initiative_modifier(self, value):
    self.hero_model.initiative_modifier = value

  def save(self):
    my_db.session.add(self.hero_model)
    my_db.session.commit()

  def get_id(self):
    return self.hero_model.id

  def get_gravatar_hash(self):
    return hashlib.md5(self.hero_model.player_name).hexdigest()



