#!python
import einit
import einit.models

#set login manager options:
einit.login_manager.login_message_category='warning'
einit.login_manager.anonymous_user=einit.models.AnonymousUser
einit.login_manager.login_view = "signin"

@einit.login_manager.user_loader
def load_user(userid):
  return einit.models.User.get_user_by_id(userid)
