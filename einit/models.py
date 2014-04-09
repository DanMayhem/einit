import einit
import Crypto.Random
import hashlib
import sqlalchemy
import sqlalchemy.orm

import flask.ext.login

my_db = einit.db

_max_level = 40
_xp_by_level = [0,100,125,150,175,200,250,300,350,400,500,600,700,800,1000,1200,1400,1600,2000,2400,2800,3200,4150,5100,6050,7000,9000,11000,13000,15000,19000,23000,27000,31000,39000,47000,55000,63000,79000,95000,111000]
_role_xp_factor = {"":1,"Standard":1,"Minion":.25,"Elite":2,"Solo":5}

class UserModel(my_db.Model):
  __tablename__ = 'users'
  id = my_db.Column(my_db.Integer, primary_key = True)
  name = my_db.Column(my_db.String(64), index = True, unique = True)
  email = my_db.Column(my_db.String(120), index = True, unique = True)
  password_digest = my_db.Column(my_db.String(64))
  session_digest = my_db.Column(my_db.String(64), index = True, unique = True)
  role = my_db.Column(my_db.SmallInteger, default = 0)

  heroes = sqlalchemy.orm.relationship("HeroModel")
  monsters = sqlalchemy.orm.relationship("MonsterModel")
  encounters = sqlalchemy.orm.relationship("EncounterModel")

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
    return sorted(map(lambda h: Hero(self, h), self.u.heroes),key=lambda h:h.hero_name)

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

  def get_monsters(self):
    return map(lambda m: Monster(self, m), self.u.monsters)

  def get_monster_count(self):
    return len(self.u.monsters)  

  def get_monster_by_id(self, monster_id):
    try:
      monster = my_db.session.query(MonsterModel).join(UserModel).filter(UserModel.id == self.u.id).filter(MonsterModel.id == monster_id).one()
      return Monster(self, monster)
    except sqlalchemy.orm.exc.NoResultFound:
      return None
    except sqlalchemy.orm.exc.MultipleResultsFound:
      return None

  def get_encounters(self):
    return sorted(map(lambda e: Encounter(self, e), self.u.encounters), key=lambda x: x.name)

  def get_encounter_count(self):
    return len(self.u.encounters)  

  def get_encounter_by_id(self, encounter_id):
    try:
      encounter = my_db.session.query(EncounterModel).join(UserModel).filter(UserModel.id == self.u.id).filter(EncounterModel.id == encounter_id).one()
      return Encounter(self, encounter)
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

class Actor(object):
  def get_category(self):
    return None

  def get_gravatar_url(self):
    return 'https://www.gravatar.com/avatar/%s'%self.get_gravatar_hash()

  def get_gravatar_hash(self):
    return hashlib.md5(self.get_display_name()).hexdigest()

  def get_max_hp(self):
    return 0

  def get_display_name(self):
    return ""

  def get_level(self):
    return 0

  def get_xp(self):
    return _xp_by_level[self.get_level()]

class HeroModel(my_db.Model):
  __tablename__='heroes'
  id = my_db.Column(my_db.Integer, primary_key = True)
  hero_name = my_db.Column(my_db.String(64))
  player_name = my_db.Column(my_db.String(66))
  level = my_db.Column(my_db.Integer)
  max_hp = my_db.Column(my_db.Integer)
  initiative_modifier = my_db.Column(my_db.Integer)

  creator_id = my_db.Column(my_db.Integer,my_db.ForeignKey('users.id'))

class Hero(Actor):
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

  def get_gravatar_url(self):
    return "%s?d=wavatar"%super(Hero,self).get_gravatar_url()

  def get_display_name(self):
    return self.hero_model.hero_name

  def get_gravatar_hash(self):
    return hashlib.md5(self.hero_model.player_name).hexdigest()

  def destroy(self):
    for e in User.get_user_by_id(self.hero_model.creator_id).get_encounters():
      e.remove_actor(self)
    my_db.session.delete(self.hero_model)
    my_db.session.commit()

  def get_xp(self):
    return _xp_by_level[int(self.level)]

  def get_category(self):
    return 'hero'

  def get_max_hp(self):
    return self.max_hp

  def get_display_name(self):
    return self.hero_name

  def get_level(self):
    return self.level


class MonsterModel(my_db.Model):
  __tablename__='monsters'
  id = my_db.Column(my_db.Integer, primary_key = True)
  name = my_db.Column(my_db.String(64))
  level = my_db.Column(my_db.Integer)
  second_role = my_db.Column(my_db.String(64))
  origin = my_db.Column(my_db.String(64))
  monster_type = my_db.Column(my_db.String(64))
  keywords = my_db.Column(my_db.String(256))
  max_hp = my_db.Column(my_db.Integer)
  initiative_modifier = my_db.Column(my_db.Integer)
  ac = my_db.Column(my_db.Integer)
  fortitude = my_db.Column(my_db.Integer)
  reflex = my_db.Column(my_db.Integer)
  will = my_db.Column(my_db.Integer)
  perception = my_db.Column(my_db.Integer)
  senses = my_db.Column(my_db.String(256))
  speed = my_db.Column(my_db.String(64))
  immune = my_db.Column(my_db.String(64))
  resist = my_db.Column(my_db.String(64))
  vulnerable = my_db.Column(my_db.String(64))
  saving_throws = my_db.Column(my_db.Integer)
  action_points = my_db.Column(my_db.Integer)
  actions = sqlalchemy.orm.relationship("MonsterActionModel")

  creator_id = my_db.Column(my_db.Integer,my_db.ForeignKey('users.id'))

class Monster(Actor):
  def __init__(self, u, mm=None):
    if mm is None:
      self.monster_model = MonsterModel()
      self.monster_model.creator_id = u.get_id()
    else:
      self.monster_model = mm

  @property
  def name(self):
    return self.monster_model.name
  @name.setter
  def name(self, value):
    self.monster_model.name = value

  @property
  def level(self):
    return self.monster_model.level
  @level.setter
  def level(self, value):
    self.monster_model.level = value

  @property
  def max_hp(self):
    return self.monster_model.max_hp
  @max_hp.setter
  def max_hp(self, value):
    self.monster_model.max_hp = value

  @property
  def initiative_modifier(self):
    return self.monster_model.initiative_modifier
  @initiative_modifier.setter
  def initiative_modifier(self, value):
    self.monster_model.initiative_modifier = value
 
  @property
  def second_role(self):
    return self.monster_model.second_role
  @second_role.setter
  def second_role(self, value):
    self.monster_model.second_role = value
 
  @property
  def origin(self):
    return self.monster_model.origin
  @origin.setter
  def origin(self, value):
    self.monster_model.origin = value

  @property
  def monster_type(self):
    return self.monster_model.monster_type
  @monster_type.setter
  def monster_type(self, value):
    self.monster_model.monster_type = value
 
  @property
  def keywords(self):
    return self.monster_model.keywords
  @keywords.setter
  def keywords(self, value):
    self.monster_model.keywords = value
 
  @property
  def ac(self):
    return self.monster_model.ac
  @ac.setter
  def ac(self, value):
    self.monster_model.ac = value

  @property
  def fortitude(self):
    return self.monster_model.fortitude
  @fortitude.setter
  def fortitude(self, value):
    self.monster_model.fortitude = value

  @property
  def reflex(self):
    return self.monster_model.reflex
  @reflex.setter
  def reflex(self, value):
    self.monster_model.reflex = value

  @property
  def will(self):
    return self.monster_model.will
  @will.setter
  def will(self, value):
    self.monster_model.will = value

  @property
  def perception(self):
    return self.monster_model.perception
  @perception.setter
  def perception(self, value):
    self.monster_model.perception = value

  @property
  def senses(self):
    return self.monster_model.senses
  @senses.setter
  def senses(self, value):
    self.monster_model.senses = value

  @property
  def speed(self):
    return self.monster_model.speed
  @speed.setter
  def speed(self, value):
    self.monster_model.speed = value

  @property
  def immune(self):
    return self.monster_model.immune
  @immune.setter
  def immune(self, value):
    self.monster_model.immune = value

  @property
  def resist(self):
    return self.monster_model.resist
  @resist.setter
  def resist(self, value):
    self.monster_model.resist = value

  @property
  def vulnerable(self):
    return self.monster_model.vulnerable
  @vulnerable.setter
  def vulnerable(self, value):
    self.monster_model.vulnerable = value

  @property
  def saving_throws(self):
    return self.monster_model.saving_throws
  @saving_throws.setter
  def saving_throws(self, value):
    self.monster_model.saving_throws = value

  @property
  def action_points(self):
    return self.monster_model.action_points
  @action_points.setter
  def action_points(self, value):
    self.monster_model.action_points = value
 
  def save(self):
    my_db.session.add(self.monster_model)
    my_db.session.commit()

  def get_id(self):
    return self.monster_model.id

  def get_gravatar_hash(self):
    return hashlib.md5(self.monster_model.name).hexdigest()

  def destroy(self):
    for e in User.get_user_by_id(self.monster_model.creator_id).get_encounters():
      e.remove_actor(self)
    my_db.session.delete(self.monster_model)
    my_db.session.commit()

  def get_xp(self):
    return _xp_by_level[int(self.level)] * _role_xp_factor[self.second_role]

  def get_action_by_id(self, action_id):
    try:
      action = my_db.session.query(MonsterActionModel).join(MonsterModel).filter(MonsterModel.id == self.monster_model.id).filter(MonsterActionModel.id == action_id).one()
      return MonsterAction(self, action)
    except sqlalchemy.orm.exc.NoResultFound:
      return None
    except sqlalchemy.orm.exc.MultipleResultsFound:
      return None

  def get_actions(self):
    return map(lambda a: MonsterAction(None, a), self.monster_model.actions)

  def get_traits(self):
    return map(lambda a: MonsterAction(None,a),filter(lambda a:a.category=='Trait',self.monster_model.actions))

  def get_moves(self):
    return map(lambda a: MonsterAction(None, a),filter(lambda a:a.category=='Move',self.monster_model.actions))

  def get_standards(self):
    return map(lambda a: MonsterAction(None, a),filter(lambda a:a.category=='Standard',self.monster_model.actions))

  def get_minors(self):
    return map(lambda a: MonsterAction(None, a),filter(lambda a:a.category=='Minor',self.monster_model.actions))

  def get_triggereds(self):
    return map(lambda a: MonsterAction(None, a),filter(lambda a:a.category=='Triggered',self.monster_model.actions))

  def get_frees(self):
    return map(lambda a: MonsterAction(None, a),filter(lambda a:a.category=='Free',self.monster_model.actions))

  def get_others(self):
    return map(lambda a: MonsterAction(None, a),filter(lambda a:a.category=='Other',self.monster_model.actions))

  def get_category(self):
    return 'monster'

  def get_gravatar_url(self):
    return '%s?d=monsterid'%(super(Monster,self).get_gravatar_url())

  def get_max_hp(self):
    return self.max_hp

  def get_display_name(self):
    return self.name

  def get_level(self):
    return level

class MonsterActionModel(my_db.Model):
  __tablename__ = 'monster_actions'
  id = my_db.Column(my_db.Integer, primary_key = True)
  category = my_db.Column(my_db.String(64))
  aura_range = my_db.Column(my_db.String(64))
  recharge = my_db.Column(my_db.String(64))
  frequency = my_db.Column(my_db.String(64))
  icon = my_db.Column(my_db.String(64))
  name = my_db.Column(my_db.String(64))
  description = my_db.Column(my_db.String(512))
  trigger = my_db.Column(my_db.String(256))
  trigger_usage = my_db.Column(my_db.String(256))
  attack = my_db.Column(my_db.String(64))
  hit = my_db.Column(my_db.String(256))
  miss = my_db.Column(my_db.String(256))
  effect = my_db.Column(my_db.String(256))
  secondary_attack = my_db.Column(my_db.String(256))
  aftereffect = my_db.Column(my_db.String(256))
  special = my_db.Column(my_db.String(512))
  keywords = my_db.Column(my_db.String(64))

  monster_id = my_db.Column(my_db.Integer,my_db.ForeignKey('monsters.id'))

class MonsterAction(object):
  def __init__(self, monster, ma=None):
    if ma is None:
      self.monster_action = MonsterActionModel()
      self.monster_action.monster_id = monster.get_id()
    else:
      self.monster_action = ma

  @property
  def category(self):
    return self.monster_action.category
  @category.setter
  def category(self, value):
    self.monster_action.category = value

  @property
  def aura_range(self):
    return self.monster_action.aura_range
  @aura_range.setter
  def aura_range(self, value):
    self.monster_action.aura_range = value
    
  @property
  def recharge(self):
    return self.monster_action.recharge
  @recharge.setter
  def recharge(self, value):
    self.monster_action.recharge = value
    
  @property
  def frequency(self):
    return self.monster_action.frequency
  @frequency.setter
  def frequency(self, value):
    self.monster_action.frequency = value
    
  @property
  def icon(self):
    return self.monster_action.icon
  @icon.setter
  def icon(self, value):
    self.monster_action.icon = value
    
  @property
  def name(self):
    return self.monster_action.name
  @name.setter
  def name(self, value):
    self.monster_action.name = value
    
  @property
  def description(self):
    return self.monster_action.description
  @description.setter
  def description(self, value):
    self.monster_action.description = value
    
  @property
  def trigger(self):
    return self.monster_action.trigger
  @trigger.setter
  def trigger(self, value):
    self.monster_action.trigger = value
    
  @property
  def trigger_usage(self):
    return self.monster_action.trigger_usage
  @trigger_usage.setter
  def trigger_usage(self, value):
    self.monster_action.trigger_usage = value
    
  @property
  def attack(self):
    return self.monster_action.attack
  @attack.setter
  def attack(self, value):
    self.monster_action.attack = value
    
  @property
  def hit(self):
    return self.monster_action.hit
  @hit.setter
  def hit(self, value):
    self.monster_action.hit = value
    
  @property
  def miss(self):
    return self.monster_action.miss
  @miss.setter
  def miss(self, value):
    self.monster_action.miss = value
    
  @property
  def effect(self):
    return self.monster_action.effect
  @effect.setter
  def effect(self, value):
    self.monster_action.effect = value
    
  @property
  def secondary_attack(self):
    return self.monster_action.secondary_attack
  @secondary_attack.setter
  def secondary_attack(self, value):
    self.monster_action.secondary_attack = value
    
  @property
  def aftereffect(self):
    return self.monster_action.aftereffect
  @aftereffect.setter
  def aftereffect(self, value):
    self.monster_action.aftereffect = value
    
  @property
  def special(self):
    return self.monster_action.special
  @special.setter
  def special(self, value):
    self.monster_action.special = value
    
  @property
  def keywords(self):
    return self.monster_action.keywords
  @keywords.setter
  def keywords(self, value):
    self.monster_action.keywords = value
    
  @property
  def monster_id(self):
    return self.monster_action.monster_id
  @monster_id.setter
  def monster_id(self, value):
    self.monster_action.monster_id = value
    
  def save(self):
    my_db.session.add(self.monster_action)
    my_db.session.commit()

  def get_id(self):
    return self.monster_action.id

  def destroy(self):
    my_db.session.delete(self.monster_action)
    my_db.session.commit()

class EncounterModel(my_db.Model):
  __tablename__ = 'encounters'
  id = my_db.Column(my_db.Integer, primary_key = True)
  name = my_db.Column(my_db.String(64))
  description = my_db.Column(my_db.String(512))
  actors = sqlalchemy.orm.relationship("ActorModel")

  creator_id = my_db.Column(my_db.Integer,my_db.ForeignKey('users.id'))

class Encounter(object):
  def __init__(self, u, em=None):
    if em is None:
      self.encounter_model = EncounterModel()
      self.encounter_model.creator_id = u.get_id()
    else:
      self.encounter_model = em

  @property
  def name(self):
    return self.encounter_model.name
  @name.setter
  def name(self, value):
    self.encounter_model.name = value
    
  @property
  def description(self):
    return self.encounter_model.description
  @description.setter
  def description(self, value):
    self.encounter_model.description = value
    
  def save(self):
    my_db.session.add(self.encounter_model)
    my_db.session.commit()

  def get_id(self):
    return self.encounter_model.id

  def destroy(self):
    my_db.session.delete(self.encounter_model)
    my_db.session.commit()

  def get_gravatar_hash(self):
    return hashlib.md5(self.encounter_model.name).hexdigest()

  def get_party_level(self):
    xp = 0
    for h in self.get_heroes():
      xp += h.get_xp()
    level = 0
    xp = xp/5
    while level < _max_level and _xp_by_level[level] < xp:
      level += 1
    return level

  def get_encounter_level(self):
    xp = 0
    for m in self.get_monsters():
      xp += m.get_xp() * self.get_actor_spawn_count(m)
    level = 0
    xp /= 5
    while level < _max_level and _xp_by_level[level] < xp:
      level += 1
    return level

  def get_difficulty(self):
    diff = self.get_encounter_level() - self.get_party_level()
    if diff < -2:
      return 'Too easy'
    elif diff < 0:
      return 'Easy'
    elif diff < 2:
      return 'Just right'
    elif diff < 4:
      return 'Hard'
    return 'Very hard'

  def get_heroes(self):
    my_user = User.get_user_by_id(self.encounter_model.creator_id)
    return sorted(
      map(lambda h: my_user.get_hero_by_id(h.reference_id),
        filter(lambda a:a.category=='hero',self.encounter_model.actors)),
      key=lambda x: x.hero_name
    )

  def get_monsters(self):
    my_user = User.get_user_by_id(self.encounter_model.creator_id)
    return sorted(
      map(lambda h: my_user.get_monster_by_id(h.reference_id),
        filter(lambda a:a.category=='monster',self.encounter_model.actors)),
      key=lambda x: x.name
    )

  def find_actor(self, category, actor_id):
    actor = None
    for am in self.encounter_model.actors:
      if am.category == category and am.reference_id == actor_id:
        actor=am
    return actor

  def get_actor_spawn_count(self, actor):
    am = self.find_actor(actor.get_category(), actor.get_id())
    if am is not None:
      return am.spawn_count
    return 0

  def add_hero(self, h):
    self.add_actor(h)

  def add_monster(self, m):
    self.add_actor(m)

  def add_actor(self, actor):
    am = self.find_actor(actor.get_category(),actor.get_id())
    if am is None:
      am = ActorModel()
      am.spawn_count = 0
    am.category=actor.get_category()
    am.reference_id = actor.get_id()
    am.spawn_count += 1
    am.initiative = None
    am.encounter_id = self.encounter_model.id
    my_db.session.add(am)
    my_db.session.commit()

  def remove_hero(self, h):
    self.remove_actor(h)

  def remove_actor(self, a):
    am = self.find_actor(a.get_category(), a.get_id())
    if am is not None:
      am.spawn_count -= 1
      if am.spawn_count <=0:
        my_db.session.delete(am)
      else:
        my_db.session.add(am)
      my_db.session.commit()

class ActorModel(my_db.Model):
  __tablename__ = 'actors'
  id = my_db.Column(my_db.Integer, primary_key = True)
  category = my_db.Column(my_db.String(64))
  reference_id = my_db.Column(my_db.Integer)
  spawn_count = my_db.Column(my_db.Integer)
  initiative = my_db.Column(my_db.Integer)

  encounter_id = my_db.Column(my_db.Integer,my_db.ForeignKey('encounters.id'))

