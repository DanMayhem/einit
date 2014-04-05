#!python

import einit
import einit.models
import einit.xml_support

u = einit.models.User.get_user_by_name('Dan')
m = einit.models.Monster(u)

x= open("bel_shalor.monster.xml").read()

einit.xml_support.monster_from_xml(x,m)

print m.name
print m.perception
print m.type
print m.max_hp
print m.speed
print m.vulnerable
print m.action_points

for a in m.get_actions():
  print a.name