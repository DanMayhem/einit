import einit


my_db = einit.db

class User(my_db.Model):
  id = my_db.Column(my_db.Integer, primary_key = True)
  name = my_db.Column(my_db.String(64), index = True, unique = True)
  email = my_db.Column(my_db.String(120), index = True, unique = True)
  password_digest = my_db.Column(my_db.String(64), index = False, unique = False)
  session_digest = my_db.Column(my_db.String(64), index = True, unique = False)
  role = my_db.Column(my_db.SmallInteger, default = 0)

  def __repr__(self):
    return '<User %r>' % (self.nickname)