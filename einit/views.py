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
  saving_throws = f.IntegerField('Saving throw modifier', validators=[v.Optional()])
  action_points = f.IntegerField('Action points', validators=[v.Optional()])

  save = f.SubmitField('Save Monster')

class MonsterActionForm(w.Form):
  category = f.SelectField('Category',choices=[
    ('Trait','Trait'),
    ('Move','Move'),
    ('Minor','Minor'),
    ('Standard','Standard'),
    ('Triggered','Triggered'),
    ('Free','Free'),
    ('Other','Other')])
  aura_range = f.StringField('Aura Range', description='for aura traits only')
  recharge = f.StringField('Recharge on', description='e.g. 5+ or "when bloodied"')
  frequency = f.SelectField('Usage',choices=[
    ('',''),
    ('At-Will','At-Will'),
    ('Encounter','Encounter'),
    ('Recharge','Recharge')
    ])
  icon = f.SelectField("Action type", choices=[
    ('none',''),
    ('melee','Melee'),
    ('melee-basic','Basic Melee'),
    ('ranged','Ranged'),
    ('ranged-basic','Basic Ranged'),
    ('close','Close'),
    ('area','Area')
    ])
  name = f.StringField('Name')
  keywords = f.StringField('Keywords')
  description = f.TextAreaField('Description')
  trigger = f.StringField('Trigger')
  trigger_usage = f.SelectField('Usage',choices=[
    ('',''),
    ('Reaction','Reaction'),
    ('Immediate Interrupt','Interrupt'),
    ('Opportunity','Opportunity'),
    ('Free','Free')
    ])
  attack = f.StringField('Attack', description="e.g. Close Burst 3 (enemies only); +12 vs AC")
  hit = f.StringField("Hit")
  miss = f.StringField("Miss")
  effect = f.StringField("Effect")
  secondary_attack = f.StringField("Secondary Attack")
  aftereffect = f.StringField("After-Effect")
  special = f.StringField("Special")

  save = f.SubmitField('Save action')

class XmlMonsterForm(w.Form):
  filename = f.FileField('.monster file')
  upload = f.SubmitField('Upload monster')

class EncounterForm(w.Form):
  name = f.StringField('Name')
  description = f.TextAreaField('Description')

  save = f.SubmitField('Save encounter')

class EncounterEventForm(w.Form):
  name = f.StringField('Name')
  description = f.TextAreaField('Description')

  save = f.SubmitField('Add event')
