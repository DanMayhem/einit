#!python
import hashlib
import xml.etree.ElementTree as ET

import einit.models
import db

_db = db._db

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
    return einit.models._xp_by_level[self.get_level()]

  def get_initiative_modifier(self):
    return 0

class Hero(Actor):
  def __init__(self, u, hm=None):
    if hm is None:
      self.hero_model = db.HeroModel()
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
    _db.session.add(self.hero_model)
    _db.session.commit()

  def get_id(self):
    return self.hero_model.id

  def get_gravatar_url(self):
    return "%s?d=wavatar"%super(Hero,self).get_gravatar_url()

  def get_display_name(self):
    return self.hero_model.hero_name

  def get_gravatar_hash(self):
    return hashlib.md5(self.hero_model.player_name).hexdigest()

  def destroy(self):
    for e in einit.users.User.get_user_by_id(self.hero_model.creator_id).get_encounters():
      e.remove_actor(self)
    _db.session.delete(self.hero_model)
    _db.session.commit()

  def get_xp(self):
    return einit.models._xp_by_level[int(self.level)]

  def get_category(self):
    return 'hero'

  def get_max_hp(self):
    return self.max_hp

  def get_display_name(self):
    return self.hero_name

  def get_level(self):
    return self.level

  def get_initiative_modifier(self):
    return self.initiative_modifier

class Monster(Actor):
  def __init__(self, u, mm=None):
    if mm is None:
      self.monster_model = db.MonsterModel()
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
    _db.session.add(self.monster_model)
    _db.session.commit()

  def get_id(self):
    return self.monster_model.id

  def get_gravatar_hash(self):
    return hashlib.md5(self.monster_model.name).hexdigest()

  def destroy(self):
    for e in einit.models.users.User.get_user_by_id(self.monster_model.creator_id).get_encounters():
      e.remove_actor(self)
    _db.session.delete(self.monster_model)
    _db.session.commit()

  def get_xp(self):
    return einit.models._xp_by_level[int(self.level)] * einit.models._role_xp_factor[self.second_role]

  def get_action_by_id(self, action_id):
    try:
      action = _db.session.query(db.MonsterActionModel).join(db.MonsterModel).filter(db.MonsterModel.id == self.monster_model.id).filter(db.MonsterActionModel.id == action_id).one()
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
    return self.level

  def get_initiative_modifier(self):
    return self.initiative_modifier

class MonsterAction(object):
  def __init__(self, monster, ma=None):
    if ma is None:
      self.monster_action = db.MonsterActionModel()
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
    _db.session.add(self.monster_action)
    _db.session.commit()

  def get_id(self):
    return self.monster_action.id

  def destroy(self):
    _db.session.delete(self.monster_action)
    _db.session.commit()


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
    return self.level

  def get_initiative_modifier(self):
    return self.initiative_modifier

class MonsterAction(object):
  def __init__(self, monster, ma=None):
    if ma is None:
      self.monster_action = db.MonsterActionModel()
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
    _db.session.add(self.monster_action)
    _db.session.commit()

  def get_id(self):
    return self.monster_action.id

  def destroy(self):
    _db.session.delete(self.monster_action)
    _db.session.commit()

def monster_from_xml(xml_string, monster):
  root = ET.fromstring(xml_string)
  monster.name = root.find("./Name").text
  monster.level = int(root.find("./Level").text)
  monster.second_role = root.find("./GroupRole//Name").text
  monster.monster_type = "%s %s %s"%(
    root.findtext("./Size//Name",""),
    root.findtext("./Origin//Name",""),
    root.findtext("./Type//Name","")
    )
  monster.keywords = ", ".join(map(lambda x: x.text,root.findall("./Keywords//Name")))
  monster.max_hp = int(root.find("./HitPoints").get('FinalValue'))
  monster.initiative_modifier = int(root.find("./Initiative").get('FinalValue'))
  for e in root.findall("./Defenses/Values/*"):
    if e.find("./Name").text=="AC":
      monster.ac = int(e.get("FinalValue"))
    if e.find("./Name").text=="Fortitude":
      monster.fortitude = int(e.get("FinalValue"))
    if e.find("./Name").text=="Reflex":
      monster.reflex = int(e.get("FinalValue"))
    if e.find("./Name").text=="Will":
      monster.will = int(e.get("FinalValue"))
  for e in root.findall("./Skills/Values/SkillNumber"):
    if e.find("./Name").text=="Perception":
      monster.perception = int(e.get("FinalValue"))
  
  #monster.senses = ", ".join(map(lambda x: x.text, root.findall("./Senses//Name")))
  temp = []
  for e in root.findall("./Senses/SenseReference"):
    if int(e.findtext("./Range","0")) > 0:
      temp.append("%s %s"%(
        e.findtext("./ReferencedObject/Name",""),
        e.findtext("./Range")))
    else:
      temp.append(e.findtext("./ReferencedObject/Name",""))
  monster.senses = '; '.join(temp)

  monster.speed = root.find("./LandSpeed/Speed").get('FinalValue')
  for e in root.findall("./Speeds/CreatureSpeed"):
    monster.speed += ", %s %s %s"%(
      e.find("./ReferencedObject/Name").text,
      e.find("./Speed").get("FinalValue"),
      e.find("./Details").text if e.find("./Details") is not None else "")

  monster.immune = ", ".join(map(lambda x:x.text, root.findall("./Immunities//Name")))
  resist_list = []
  for e in root.findall("./Resistances/CreatureSusceptibility"):
    resist_list.append("%s %s %s"%(
      e.find("./Amount").get("FinalValue"),
      e.find("./ReferencedObject/Name").text,
      e.findtext("./Details","")))
  monster.resist = "; ".join(resist_list)
  vulnerable_list = []
  for e in root.findall("./Weaknesses/CreatureSusceptibility"):
    vulnerable_list.append("%s %s %s"%(
      e.find("./Amount").get("FinalValue"),
      e.find("./ReferencedObject/Name").text,
      e.findtext("./Details","")))
  monster.vulnerable = "; ".join(vulnerable_list)
  monster.saving_throws = int(root.find("./SavingThrows/MonsterSavingThrow").get("FinalValue"))
  monster.action_points = int(root.find("./ActionPoints").get("FinalValue"))

  monster.save()

  for e in root.findall("./Powers/MonsterTrait"):
    monster_trait_from_xml(e, monster)

  for e in root.findall("./Powers/MonsterPower"):
    monster_power_from_xml(e, monster)


def monster_trait_from_xml(root, monster):
  a = einit.models.MonsterAction(monster)
  #handle differently base on action:
  a.category="Trait"
  a.aura_range=""
  r = root.find("./Range")
  if r is not None:
    a.aura_range = r.get("FinalValue")
  if int(a.aura_range)==0:
    a.aura_range=""
  a.recharge = ""
  a.frequency = ""
  a.icon = ""
  a.name = root.findtext("./Name")
  a.description = root.findtext("./Details")
  a.trigger=""
  a.attack=""
  a.hit=""
  a.miss=""
  a.effect=""
  a.secondary_attack=""
  a.aftereffect=""
  a.special=""
  a.keywords = ", ".join(map(lambda x: x.text, root.findall("./Keywords//Name")))
  a.save()

def monster_power_from_xml(root, monster):
  a = einit.models.MonsterAction(monster)
  #handle differently base on action:
  if root.find("./Trigger") is not None:
    a.category = "Triggered"
    a.trigger_usage = root.findtext("./Action","")
    a.aura_range = ""
    a.recharge = ""
    a.frequency = root.findtext("./Usage","")
    a.icon = ""
    a.name = root.findtext("./Name","")
    a.description = root.findtext("./FlavorText","")
    a.trigger=root.findtext("./Trigger","")
    a.attack = ""
    temp = root.find("./Attacks/MonsterAttack/AttackBonuses/MonsterPowerAttackNumber")
    if temp is not None:
      temp = temp.get('FinalValue')
      if root.findtext("./Attacks/MonsterAttack/Range","") != "":
        a.attack= "%s; +%s vs. %s"%(
          root.findtext("./Attacks/MonsterAttack/Range",""),
          temp,
          root.findtext("./Attacks/MonsterAttack/AttackBonuses/MonsterPowerAttackNumber/Defense/ReferencedObject/DefenseName",""))
      else:
        a.attack= "+%s vs. %s"%(
          temp,
          root.findtext("./Attacks/MonsterAttack/AttackBonuses/MonsterPowerAttackNumber/Defense/ReferencedObject/DefenseName",""))

    a.hit= " ".join([root.findtext("./Attacks/MonsterAttack/Hit/Damage/Expression",""),
                     root.findtext("./Attacks/MonsterAttack/Hit/Description","")])
    a.miss= " ".join([root.findtext("./Attacks/MonsterAttack/Miss/Damage/Expression",""),
                      root.findtext("./Attacks/MonsterAttack/Miss/Description","")])
    a.effect= root.findtext("./Attacks/MonsterAttack/Effect/Description","")
    a.secondary_attack=""
    a.aftereffect=""
    a.special=""
    a.keywords = ", ".join(map(lambda x: x.text, root.findall("./Keywords//Name")))
  elif root.findtext("./Action") in ['Move','Minor','Standard','Free']:
    a.category = root.findtext("./Action")
    a.aura_range = ""
    a.recharge = ""
    if root.findtext("./Usage")=="Recharge":
      a.recharge = root.findtext("./UsageDetails","")
    a.frequency = root.findtext("./Usage","")
    a.icon = ""
    a.name = root.findtext("./Name","")
    a.description = root.findtext("./FlavorText","")
    a.trigger = ""
    a.trigger_usage = ""
    a.attack = ""
    temp = root.find("./Attacks/MonsterAttack/AttackBonuses/MonsterPowerAttackNumber")
    if temp is not None:
      temp = temp.get('FinalValue')
      if root.findtext("./Attacks/MonsterAttack/Range","") != "":
        a.attack= "%s; +%s vs. %s"%(
          root.findtext("./Attacks/MonsterAttack/Range",""),
          temp,
          root.findtext("./Attacks/MonsterAttack/AttackBonuses/MonsterPowerAttackNumber/Defense/ReferencedObject/DefenseName",""))
      else:
        a.attack= "+%s vs. %s"%(
          temp,
          root.findtext("./Attacks/MonsterAttack/AttackBonuses/MonsterPowerAttackNumber/Defense/ReferencedObject/DefenseName",""))

    a.hit= " ".join([root.findtext("./Attacks/MonsterAttack/Hit/Damage/Expression",""),
                     root.findtext("./Attacks/MonsterAttack/Hit/Description","")])
    a.miss= " ".join([root.findtext("./Attacks/MonsterAttack/Miss/Damage/Expression",""),
                      root.findtext("./Attacks/MonsterAttack/Miss/Description","")])
    a.effect= root.findtext("./Attacks/MonsterAttack/Effect/Description","")
    a.secondary_attack = ""
    a.aftereffect = ""
    a.special = ""
    a.keywords = ", ".join(map(lambda x: x.text, root.findall("./Keywords//Name")))
  else:
    a.category = "Other"
    a.aura_range = ""
    a.recharge = ""
    if root.findtext("./Usage")=="Recharge":
      a.recharge = root.findtext("./UsageDetails","")
    a.frequency = root.findtext("./Usage","")
    a.icon = ""
    a.name = root.findtext("./Name","")
    a.description = " ".join([root.findtext("./Action"),root.findtext("./FlavorText","")])
    a.trigger = ""
    a.trigger_usage = ""
    a.attack = ""
    temp = root.find("./Attacks/MonsterAttack/AttackBonuses/MonsterPowerAttackNumber")
    temp = root.find("./Attacks/MonsterAttack/AttackBonuses/MonsterPowerAttackNumber")
    if temp is not None:
      temp = temp.get('FinalValue')
      if root.findtext("./Attacks/MonsterAttack/Range","") != "":
        a.attack= "%s; +%s vs. %s"%(
          root.findtext("./Attacks/MonsterAttack/Range",""),
          temp,
          root.findtext("./Attacks/MonsterAttack/AttackBonuses/MonsterPowerAttackNumber/Defense/ReferencedObject/DefenseName",""))
      else:
        a.attack= "+%s vs. %s"%(
          temp,
          root.findtext("./Attacks/MonsterAttack/AttackBonuses/MonsterPowerAttackNumber/Defense/ReferencedObject/DefenseName",""))

    a.hit= " ".join([root.findtext("./Attacks/MonsterAttack/Hit/Damage/Expression",""),
                     root.findtext("./Attacks/MonsterAttack/Hit/Description","")])
    a.miss= " ".join([root.findtext("./Attacks/MonsterAttack/Miss/Damage/Expression",""),
                      root.findtext("./Attacks/MonsterAttack/Miss/Description","")])
    a.effect= root.findtext("./Attacks/MonsterAttack/Effect/Description","")
    a.secondary_attack = ""
    a.aftereffect = ""
    a.special = ""
    a.keywords = ", ".join(map(lambda x: x.text, root.findall("./Keywords//Name")))


  a.save()

