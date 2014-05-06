#!python

_max_level = 40
_xp_by_level = [0,100,125,150,175,200,250,300,350,400,500,600,700,800,1000,1200,1400,1600,2000,2400,2800,3200,4150,5100,6050,7000,9000,11000,13000,15000,19000,23000,27000,31000,39000,47000,55000,63000,79000,95000,111000]
_role_xp_factor = {"":1,"Standard":1,"Minion":.25,"Elite":2,"Solo":5}
_statuses = "Bloodied Dominated Stunned Dazed Weakened Blinded Prone Immobilized Slowed Marked Dying Unconscious Helpless Surprised Petrified Restrained Deafened Grabbed".split()
_statuses.append(["Removed from play","Ongoing damage"])

tag = 'tag'
glyph = 'glyph'
description = 'description'
grants_combat_advantage = 'grants_combat_advantage'
can_flank = 'can_flank'
can_act = 'can_act'

_status_map = {
  'bloodied':{
    tag:'Bloodied',
    glyph:'glyphicon glyphicon-tint',
    description:'Less than half HP',
    grants_combat_advantage:False,
    can_flank:True,
    can_act:True
  },
  'stunned':{
    tag:'Stunned',
    glyph:'glyphicon glyphicon-remove-sign',
    description:'',
    grants_combat_advantage:True,
    can_flank:False,
    can_act:False
  },
  'dazed':{
    tag:'Dazed',
    glyph:'glyphicon glyphicon-question-sign',
    description:"Can only take 1 action per turn",
    grants_combat_advantage:True,
    can_flank:False,
    can_act:True
  },
  'weakened':{
    tag:'Weakened',
    glyph:'glyphicon glyphicon-minus-sign',
    description:"Attacks deal half damage",
    grants_combat_advantage:False,
    can_flank:True,
    can_act:True
  },
  'ongoing_damage':{
    tag:'DOT',
    glyph:'glyphicon glyphicon-time',
    description:"Damage taken at the start of turn",
    grants_combat_advantage:False,
    can_flank:True,
    can_act:True
  }
}

_status_list = _status_map.keys()
_status_list.sort()

status_list = _status_list
status_details = _status_map

import db

from einit.models.users import User, AnonymousUser
from einit.models.actors import Actor, Hero, Monster, MonsterAction, monster_from_xml
from einit.models.encounters import Encounter, EncounterEvent, EncounterEntry
