import flask.ext.wtf as w
import wtforms as f
import wtforms.validators as v
import wtforms.widgets

import einit.models

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

class EncounterActorStartForm(w.Form):
  actor_category = f.HiddenField('actor_category')
  actor_id = f.IntegerField('actor_id', widget=wtforms.widgets.HiddenInput())

  starting_hp = f.IntegerField('Starting hp')
  initiative = f.IntegerField('Initiative value')

class EncounterEventStartForm(w.Form):
  event_id = f.IntegerField('event_id', widget=wtforms.widgets.HiddenInput())

  initiative = f.IntegerField('Initiative value')

class EncounterStartForm(w.Form):
  actors = f.FieldList(f.FormField(EncounterActorStartForm,""),"")
  events = f.FieldList(f.FormField(EncounterEventStartForm,""),"")

  start = f.SubmitField('Start encounter')

class ModifyHitPointsForm(w.Form):
  amount = f.IntegerField("")
  action = f.SelectField('Action',choices=[
    ('damage','Damage'),
    ('temp_hp','Temp HP'),
    ('heal','Heal')
    ])


def render_encounter_as_dict(encounter):
  e = {}
  e["title"] = encounter.name
  e["round"] = encounter.round
  e["entries"] = []
  for i in encounter.get_encounter_entries():
    if i.visible:
      ent = {}
      ent['prefix_glyph']="glyphicon"
      status_list = i.get_statuses()
      ent['status_count'] = len(status_list)
      ent['status_list'] = []
      ent['has_hp'] = False
      for status in status_list:
        ent['status_list'].append({
          'glyph': einit.models.status_details[status]['glyph'],
          'descr': "%s: %s"%(einit.models.status_details[status]['tag'],einit.models.status_details[status]['description'])
          })
      if i.category == encounter.get_current_entry().category and i.reference_id == encounter.get_current_entry().reference_id :
        ent['prefix_glyph']="glyphicon glyphicon-play"
      if i.category == "event":
        event = encounter.get_event_by_id(i.reference_id)
        ent["name"]= event.name
        ent['gravatar_url']=""
      else:
        actor = encounter.get_actor_by_category_id(i.category, i.reference_id)
        ent["name"] = actor.get_display_name()
        ent['gravatar_url'] = actor.get_gravatar_url()
        if i.category == "hero":
          ent["has_hp"] = True
          max_hp = actor.get_max_hp()
          actual_hp = i.hp
          temp_hp = i.temp_hp
          if (actual_hp+temp_hp) > max_hp:
            max_hp = actual_hp + temp_hp
          hp_pcnt = (100*actual_hp)/max_hp
          temp_pcnt = (100*temp_hp)/max_hp
          if hp_pcnt < 5:
            hp_pcnt = 5
          if temp_pcnt < 5 and temp_hp > 0:
            temp_pcnt = 5
          if (hp_pcnt + temp_pcnt)>100:
            if hp_pcnt > temp_pcnt:
              hp_pcnt = 100-temp_pcnt
            else:
              temp_pcnt = 100-hp_pcnt
          ent['actual_hp']=actual_hp
          ent['temp_hp']=temp_hp
          ent['hp_pcnt']=hp_pcnt
          ent['temp_pcnt']=temp_pcnt
      e["entries"].append(ent)
  return e
