#!python
import einit
import einit.models
import sqlalchemy

#set login manager options:
einit.login_manager

@flask.ext.login.user_loader
def load_user(userid):
  try:
    u = einit.db.session.query(einit.Models.User).filter(einit.Models.User.id == userid).one()
    return u
  except sqlalchemy.orm.exc.NoResultFound:
    return None
  except sqlalchemy.orm.exc.MultipleResultsFound:
    return None
