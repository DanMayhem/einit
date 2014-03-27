import einit
import Crypto.Random
import hashlib

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
  def __init__(self, name, email, password):
    self.u = UserModel(name, email, password)

  def __repr__(self):
      return '<User %r>' %self.u.name

  def save(self):
    my_db.session.add(self.u)
    my_db.session.commit()

  def does_username_exist(name):
    return len(my_db.session.query(UserMode).filter(UserModel.name == name).all())>0
    
  def does_email_exist(email):
    return len(my_db.session.query(UserMode).filter(UserModel.email == email).all())>0
    


