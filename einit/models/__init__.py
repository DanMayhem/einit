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
    glyph:'glyphicon glyphicon-resize-small',
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
  },
  'knocked_out':{
    tag:'Knocked Out',
    glyph:'glyphletters glyphletters-ko',
    description:"Knocked out, must make death saving throws",
    grants_combat_advantage:True,
    can_flank:False,
    can_act:False
  },
  'death_save_1':{
    tag:'Death 1',
    glyph:'glyphicon glyphicon-remove',
    description:"1 failed saving throw",
    grants_combat_advantage:True,
    can_flank:False,
    can_act:False
  },
  'death_save_2':{
    tag:'Death 2',
    glyph:'glyphicon glyphicon-remove',
    description:"2 failed saving throws",
    grants_combat_advantage:True,
    can_flank:False,
    can_act:False
  },
  'death_save_3':{
    tag:'Death 3',
    glyph:'glyphicon glyphicon-remove',
    description:"3 failed saving throws",
    grants_combat_advantage:True,
    can_flank:False,
    can_act:False
  },
  'immobilized':{
    tag:'Immobilized',
    glyph:'glyphicon glyphicon-minus-sign',
    description:'You cannot move. (You can teleport or be pushed, pulled slid)',
    grants_combat_advantage:False,
    can_flank:True,
    can_act:True
  },
  'deafened':{
    tag:'Deafened',
    glyph:'glyphicon glyphicon-volume-off',
    description:'You cannot hear, -10 to perception checks.',
    grants_combat_advantage:False,
    can_flank:True,
    can_act:True
  },
  'dominated':{
    tag:'Dominated',
    glyph:'glyphicon glyphicon-user',
    description:'You are DAZED. The creature cominating you may force you to take a single at-will action on your turn. You may not take immediate actions or opportunity actions.',
    grants_combat_advantage:True,
    can_flank:False,
    can_act:False
  },
  'grabbed':{
    tag:'Grabbed',
    glyph:'glyphicon glyphicon-bullhorn',
    description:'You are IMMOBILIZED, You are no longer grabbed if the creature grabbing you is prevernted from taking actions.',
    grants_combat_advantage:False,
    can_flank:True,
    can_act:True
  },
  'prone':{
    tag:'Prone',
    glyph:'glyphicon glyphicon-arrow-down',
    description:'-2 to attack. Grant combat advantage to melee. +2 defense from ranged attacks.',
    grants_combat_advantage:True,
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
