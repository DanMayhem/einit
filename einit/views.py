import flask.ext.wtf as w
import wtforms as f
import wtforms.validators as v

class SignUpForm(w.Form):
  name = f.StringField('Name', validators=[
    v.InputRequired('Name is required field')
  ])
  email = f.StringField('Email',validators=[
    v.Email('Valid email address required')
  ])
  password = f.PasswordField('Password', validators=[
    v.InputRequired('Password required'),
    v.EqualTo('password_confirmation','Passwords must match')
  ])
  password_confirmation = f.PasswordField('Confirm Password')

  signup = f.SubmitField('Sign up')

class SignInForm(w.Form):
  name_or_email = f.StringField('Name or Email', validators=[
    v.InputRequired('Enter name or email address')
  ])
  password = f.PasswordField('Password', validators=[
    v.InputRequired('Password Required')
  ])

  login = f.SubmitField('Sign In')

class HeroForm(w.Form):
  hero_name = f.StringField('Hero Name', validators=[
    v.InputRequired('Hero name required'),
  ])
  player_name = f.StringField('Player Name', validators=[
    v.InputRequired('Player name required'),
  ])
  level = f.IntegerField('Level', validators=[
    v.InputRequired('Level required'),
  ])
  max_hp = f.IntegerField('Max Hit Points', validators=[
    v.InputRequired('Max hit hoints required'),
  ])
  initiative_modifier = f.IntegerField('Initiative Modifier', validators=[
    v.InputRequired('Initiative Modifier required'),
  ])

  save = f.SubmitField('Save Hero')

class MonsterForm(w.Form):
  name = f.StringField('Name')
  level = f.IntegerField('Level')
  second_role = f.SelectField('Role',choices=[('Standard','Standard'),('Minion','Minion'),('Elite','Elite'),('Solo','Solo')])
  origin = f.StringField('Origin')
  monster_type = f.StringField('Monster type')
  keywords = f.StringField('Keywords')
  max_hp = f.IntegerField('Max HP')
  initiative_modifier = f.IntegerField('Initiative Modifier')
  ac = f.IntegerField('AC')
  fortitude = f.IntegerField('Fortitude')
  reflex = f.IntegerField('Reflex')
  will = f.IntegerField('Will')
  perception = f.IntegerField('Perception')
  senses = f.StringField('Senses')
  speed = f.StringField('Speed')
  immune = f.StringField('Immunities')
  resist = f.StringField('Resistances')
  vulnerable = f.StringField('Vulnerabilities')
  saving_throws = f.IntegerField('Saving throw modifier')
  action_points = f.IntegerField('Action points')

  save = f.SubmitField('Save Monster')
