import einit
import Crypto.Random
import hashlib
import sqlalchemy

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