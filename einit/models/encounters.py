#!python
import hashlib
import random
import sqlalchemy.orm.exc

import einit.models
import db
import users

_db = db._db
_category_rank={'hero':1,'monster':2,'event':3}

class Encounter(object):
  def __init__(self, u, em=None):
    if em is None:
      self.encounter_model = db.EncounterModel()
      self.encounter_model.creator_id = u.get_id()
    else:
      self.encounter_model = em

  @staticmethod
  def get_encounter_by_hash(hash):
    try:
      em = _db.session.query(db.EncounterModel).filter(db.EncounterModel.hash_key == hash).one()
      return Encounter(None,em)
    except sqlalchemy.orm.exc.NoResultFound:
      return None
    except sqlalchemy.orm.exc.MultipleResultsFound:
      return None

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
    
  @property
  def round(self):
    return self.encounter_model.round
  @round.setter
  def round(self, value):
    self.encounter_model.round = value
    
  @property
  def current_entry(self):
    return self.encounter_model.current_entry
  @current_entry.setter
  def current_entry(self, value):
    self.encounter_model.current_entry = value
    
  def save(self):
    _db.session.add(self.encounter_model)
    _db.session.commit()

  def get_id(self):
    return self.encounter_model.id

  def destroy(self):
    self.abandon()
    _db.session.delete(self.encounter_model)
    _db.session.commit()

  def get_gravatar_hash(self):
    return hashlib.md5(self.encounter_model.name).hexdigest()

  def get_party_level(self):
    xp = 0
    for h in self.get_heroes():
      xp += h.get_xp()
    level = 0
    xp = xp/5
    while level < einit.models._max_level and einit.models._xp_by_level[level] < xp:
      level += 1
    return level

  def get_encounter_level(self):
    xp = 0
    for m in self.get_monsters():
      xp += m.get_xp() * self.get_actor_spawn_count(m)
    level = 0
    xp /= 5
    while level < einit.models._max_level and einit.models._xp_by_level[level] < xp:
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
    my_user = users.User.get_user_by_id(self.encounter_model.creator_id)
    return sorted(
      map(lambda h: my_user.get_hero_by_id(h.reference_id),
        filter(lambda a:a.category=='hero',self.encounter_model.actors)),
      key=lambda x: x.hero_name
    )

  def get_monsters(self):
    my_user = users.User.get_user_by_id(self.encounter_model.creator_id)
    return sorted(
      filter( lambda y: y is not None, 
        map(lambda h: my_user.get_monster_by_id(h.reference_id),
          filter(lambda a: a.category=='monster',self.encounter_model.actors))),
      key=lambda x: x.name
    )

  def get_actor_by_category_id(self, category, id):
    my_user = einit.models.users.User.get_user_by_id(self.encounter_model.creator_id)
    if category == 'hero':
      return my_user.get_hero_by_id(id)
    if category == 'monster':
      return my_user.get_monster_by_id(id)
    return None

  def _find_actor(self, category, actor_id):
    actor = None
    for am in self.encounter_model.actors:
      if am.category == category and am.reference_id == actor_id:
        actor=am
    return actor

  def get_actor_spawn_count(self, actor):
    am = self._find_actor(actor.get_category(), actor.get_id())
    if am is not None:
      return am.spawn_count
    return 0

  def add_hero(self, h):
    self.add_actor(h)

  def add_monster(self, m):
    self.add_actor(m)

  def add_actor(self, actor):
    am = self._find_actor(actor.get_category(),actor.get_id())
    if am is None:
      am = db.ActorModel()
      am.spawn_count = 0
    am.category=actor.get_category()
    am.reference_id = actor.get_id()
    am.spawn_count += 1
    am.initiative = None
    am.encounter_id = self.encounter_model.id
    _db.session.add(am)
    _db.session.commit()
    self.abandon()

  def spawn_monster(self, monster):
    if self.round == 0:
      return
    if monster.get_category()!='monster':
      return
    am = self._find_actor('monster',monster.get_id())
    if am is None:
      return
    am.spawn_count = am.spawn_count + 1
    _db.session.add(am) #update the spawn count
    _db.session.commit()
    entry = EncounterEntry(self)
    entry.spawn_index = am.spawn_count-1
    entry.hp = monster.get_max_hp()
    entry.temp_hp = 0
    entry.visible = True
    entry.category="monster"
    entry.reference_id = monster.get_id()
    entries = self.get_encounter_entries()
    #copy initiative value from another entry
    for e in entries:
      if e.category==entry.category and e.reference_id==entry.reference_id:
        entry.initiative = e.initiative
    entry.save()
    entries.append(entry)
    entries.sort(key=EncounterEntry.sort_str)
    for i in range(0,len(entries)):
      entries[i].initiative_order = i
      entries[i].save()
    self.save()

  def remove_hero(self, h):
    self.remove_actor(h)

  def remove_actor(self, a):
    am = self._find_actor(a.get_category(), a.get_id())
    if am is not None:
      am.spawn_count -= 1
      if am.spawn_count <=0:
        _db.session.delete(am)
      else:
        _db.session.add(am)
      _db.session.commit()
    self.abandon()

  def get_events(self):
    return sorted(
      map(
        lambda e: EncounterEvent(self, e), self.encounter_model.events),
      key=lambda x: x.name)

  def add_event(self, name, description):
    ee = EncounterEvent(self)
    ee.name = name
    ee.description = description
    ee.save()
    self.abandon()

  def get_event_by_id(self, event_id):
    for e in self.get_events():
      if e.get_id() == event_id:
        return e
    return None

  def get_encounter_entries(self):
    return sorted(
      map(
        lambda e: EncounterEntry(self, e), self.encounter_model.entries),
      key=EncounterEntry.sort_str)

  def get_entry_by_id(self, id):
    rval = None
    for entry in self.get_encounter_entries():
      if entry.get_id() == id:
        rval = entry
        break
    return entry

  def get_current_entry(self):
    return self.get_entry_by_id(self.current_entry)

  def get_next_entry_id(self):
    round = self.round
    entries = self.get_encounter_entries()
    for i in reversed(range(0,len(entries))):
      if self.get_current_entry().category == entries[i].category and self.get_current_entry().reference_id==entries[i].reference_id:
        break
    i = i+1
    if i >= len(entries):
      i=0
      round = round + 1
    return (round, entries[i].get_id())

  def get_prev_entry_id(self):
    round = self.round
    entries = self.get_encounter_entries()
    for i in range(0,len(entries)):
      if self.get_current_entry().category == entries[i].category and self.get_current_entry().reference_id==entries[i].reference_id:
        break
    i = i-1
    if i <0:
      round = round - 1
    return (round, entries[i].get_id())

  def set_current_event(self, round, entry_id):
    self.round = round
    self.current_entry = entry_id
    self.save()

  def abandon(self):
    self.round=0
    self.current_entry = 0
    for e in self.get_encounter_entries():
      e.destroy()
    self.encounter_model.hash_key = None
    self.save()

  def _gen_hash_key(self):
    key_values = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    return ''.join(random.sample(key_values,5))

  def get_encounter_hash_key(self):
    return self.encounter_model.hash_key

  def start(self, entries):
    """initializes the encounter"""
    #first delete any leftovers from previous runs of the encounter
    self.abandon()
    self.round=1
    entries.sort(key=EncounterEntry.sort_str)
    for i in range(0,len(entries)):
      entries[i].initiative_order = i
      entries[i].save()
    self.current_entry = entries[0].get_id()
    self.encounter_model.hash_key = self._gen_hash_key()
    while Encounter.get_encounter_by_hash(self.encounter_model.hash_key) is not None:
      self.encounter_model.hash_key = self._gen_hash_key()
    self.save()

class EncounterEvent(object):
  def __init__(self, e, ee=None):
    if ee is None:
      self.encounter_event = db.EventModel()
      self.encounter_event.encounter_id = e.get_id()
    else:
      self.encounter_event = ee

  @property
  def name(self):
    return self.encounter_event.name
  @name.setter
  def name(self, value):
    self.encounter_event.name = value
    
  @property
  def description(self):
    return self.encounter_event.description
  @description.setter
  def description(self, value):
    self.encounter_event.description = value
    
  def save(self):
    _db.session.add(self.encounter_event)
    _db.session.commit()

  def get_id(self):
    return self.encounter_event.id

  def destroy(self):
    _db.session.delete(self.encounter_event)
    _db.session.commit()

class EncounterEntry(object):
  def __init__(self, e, ee=None):
    self._sort_string = None
    if ee is None:
      self.encounter_entry = db.EncounterEntryModel()
      self.encounter_entry.encounter_id = e.get_id()
    else:
      self.encounter_entry = ee

  @property
  def initiative(self):
    return self.encounter_entry.initiative
  @initiative.setter
  def initiative(self, value):
    self.encounter_entry.initiative = value

  @property
  def initiative_order(self):
    return self.encounter_entry.initiative_order
  @initiative_order.setter
  def initiative_order(self, value):
    self.encounter_entry.initiative_order = value

  @property
  def spawn_index(self):
    return self.encounter_entry.spawn_index
  @spawn_index.setter
  def spawn_index(self, value):
    self.encounter_entry.spawn_index = value

  @property
  def hp(self):
    return self.encounter_entry.hp
  @hp.setter
  def hp(self, value):
    self.encounter_entry.hp = value

  @property
  def temp_hp(self):
    return self.encounter_entry.temp_hp
  @temp_hp.setter
  def temp_hp(self, value):
    self.encounter_entry.temp_hp = value

  @property
  def visible(self):
    if self.encounter_entry.visible == 0:
      return False
    return True
  @visible.setter
  def visible(self, value):
    if value:
      self.encounter_entry.visible = 1
    else:
      self.encounter_entry.visible = 0

  @property
  def category(self):
    return self.encounter_entry.category
  @category.setter
  def category(self, value):
    self.encounter_entry.category = value

  @property
  def reference_id(self):
    return self.encounter_entry.reference_id
  @reference_id.setter
  def reference_id(self, value):
    self.encounter_entry.reference_id = value

  def sort_str(self):
    if self._sort_string is None:
      self._sort_string = "%3d%1d%9d%2d"%(
        999-self.encounter_entry.initiative,
        _category_rank[self.encounter_entry.category],
        self.encounter_entry.reference_id,
        self.encounter_entry.spawn_index)
    return self._sort_string

  def get_id(self):
    return int(self.encounter_entry.id)

  def save(self):
    _db.session.add(self.encounter_entry)
    _db.session.commit()

  def destroy(self):
    _db.session.delete(self.encounter_entry)
    _db.session.commit()

  def apply_damage(self, hp):
    if self.temp_hp >= hp:
      self.temp_hp -= hp
    else:
      self.hp -= (hp-self.temp_hp)
      self.temp_hp = 0

    try:
      encounter = Encounter(None,
      _db.session.query(db.EncounterModel).filter(db.EncounterModel.id == self.encounter_entry.encounter_id).one())
    except sqlalchemy.orm.exc.NoResultFound:
      return None
    except sqlalchemy.orm.exc.MultipleResultsFound:
      return None

    actor = encounter.get_actor_by_category_id(self.category,self.reference_id)

    if actor and self.hp < (actor.get_max_hp()/2):
      self.set_status('bloodied')

    if actor and ((self.hp + self.temp_hp) <= 0):
      self.set_status("knocked_out")

  def apply_heal(self, hp):
    try:
      encounter = Encounter(None,
      _db.session.query(db.EncounterModel).filter(db.EncounterModel.id == self.encounter_entry.encounter_id).one())
    except sqlalchemy.orm.exc.NoResultFound:
      return None
    except sqlalchemy.orm.exc.MultipleResultsFound:
      return None

    actor = encounter.get_actor_by_category_id(self.category,self.reference_id)

    if (self.hp+hp) > actor.get_max_hp():
      self.hp = actor.get_max_hp()
    else:
      self.hp += hp


  def apply_temp_hp(self, hp):
    self.temp_hp += hp

  def set_status(self, status):
    if not self.has_status(status) and status in einit.models._status_list:
      eesm = db.EncounterEntryStatusModel()
      eesm.status = status
      eesm.encounter_entry_id = self.encounter_entry.id
      _db.session.add(eesm)

  def clear_status(self, status):
    for s in self.encounter_entry.statuses:
      if s.status == status:
        _db.session.delete(s)

  def has_status(self, status):
    return status in (self.get_statuses())

  def get_statuses(self):
    return map(lambda s: s.status, self.encounter_entry.statuses)