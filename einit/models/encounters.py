#!python
import hashlib

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
    
  def save(self):
    _db.session.add(self.encounter_model)
    _db.session.commit()

  def get_id(self):
    return self.encounter_model.id

  def destroy(self):
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
      map(lambda h: my_user.get_monster_by_id(h.reference_id),
        filter(lambda a:a.category=='monster',self.encounter_model.actors)),
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

  def get_event_by_id(self, event_id):
    for e in self.get_events():
      if e.get_id() == event_id:
        return e
    return None

  def get_encounter_entries(self):
    return sorted(
      map(
        lambda e: EncounterEntry(self, e), self.encounter_model.entries),
      key=lambda x: x.initiative_order)

  def abandon(self):
    self.round=0
    for e in self.get_encounter_entries():
      e.destroy()
    self.save()

  def start(self, events):
    """initializes the encounter"""
    #first delete any leftovers from previous runs of the encounter
    self.abandon()
    self.round=1
    events.sort()
    for i in range(0,len(events)):
      events[i].initiative_order = i
      events[i].save()
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

  def save(self):
    _db.session.add(self.encounter_entry)
    _db.session.commit()

  def destroy(self):
    _db.session.delete(self.encounter_entry)
    _db.session.commit()

  def __lt__(self, other):
    lhs = self.encounter_entry
    rhs = other.encounter_entry
    if lhs.initiative == rhs.initiative:
      if lhs.category==rhs.category:
        if lhs.reference_id==rhs.reference_id:
          return lhs.spawn_index < rhs.spawn_index
        return lhs.reference_id < rhs.reference_id
      return self._category_rank[lhs.category]<self._category_rank[rhs.category]
    return lhs.initiative<rhs.initiative


