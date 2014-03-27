#!python
import sqlalchemy

import einit
import einit.models

#set login manager options:
einit.login_manager.login_message_category='warning'
einit.login_manager.anonymous_user=einit.models.AnonymousUser

@einit.login_manager.user_loader
def load_user(userid):
  try:
    u = einit.models.load_user_by_id(userid)
    return u
  except sqlalchemy.orm.exc.NoResultFound:
    return None
  except sqlalchemy.orm.exc.MultipleResultsFound:
    return None
