#!python
import xml.etree.ElementTree as ET

import einit.models

def monster_from_xml(xml_string, monster):
  root = ET.fromstring(xml_string)
  monster.name = root.find("./Name").text
  monster.level = int(root.find("./Level").text)
  monster.second_role = root.find("./GroupRole//Name").text
  monster.monster_type = "%s %s %s"%(
    root.find("./Size//Name").text,
    root.find("./Origin//Name").text,
    root.find("./Type//Name").text
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
      a.attack= "%s; +%s vs. %s"%(
        root.findtext("./Attacks/MonsterAttack/Range",""),
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
      a.attack= "%s; +%s vs. %s"%(
        root.findtext("./Attacks/MonsterAttack/Range",""),
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
    if temp is not None:
      temp = temp.get('FinalValue')
      a.attack= "%s; +%s vs. %s"%(
        root.findtext("./Attacks/MonsterAttack/Range",""),
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

