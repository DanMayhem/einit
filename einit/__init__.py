import os
import random
import base64
import hashlib

import flask
import flask.ext.sqlalchemy
import flask.ext.login
import flask_bootstrap
import flask_sslify
import flaskext.bcrypt
import flask_redis

import Crypto.Random


app = flask.Flask(__name__)

#set debug mode and other config options as appropriate
if os.environ.has_key("DEBUG_EINIT"):
  app.debug=True
app.config['CSRF_ENABLED'] = True

#load databases
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL',"sqllite://")
#app.config['SQLALCHEMY_MIGRATE_REPO'] = os.path.join(os.path.abspath(os.path.split(os.path.dirname(__file__))[0]),'migrations')
app.config['REDIS_URL']=os.environ.get('REDISTOGO_URL')
db = flask.ext.sqlalchemy.SQLAlchemy(app)

#load secure token
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

#other flask extensions
sslify = flask_sslify.SSLify(app) #requires SSL
bcrypt = flaskext.bcrypt.Bcrypt(app) #password digests
bootstrap = flask_bootstrap.Bootstrap(app) #make bootstrap templates and helpers available.
login_manager = flask.ext.login.LoginManager(app) #login manager
redis = flask_redis.Redis(app) #redis

#import models, views and helpers
import einit.views
import einit.models

app.config['status_list'] = einit.models.status_list
app.config['status_map'] = einit.models.status_details

#set login manager options:
login_manager.login_message_category='warning'
login_manager.anonymous_user=einit.models.AnonymousUser
login_manager.login_view = "signin"

#register static routes
@app.route('/')
@app.route('/index')
def index():
  if flask.ext.login.current_user.is_authenticated():
    return flask.redirect(flask.url_for('hero'))
  return flask.render_template("index.html")

#user routes
@app.route('/signup', methods=['GET','POST'])
def signup():
  form = einit.views.SignUpForm()
  if form.validate_on_submit():
    #check to see if usename exists:
    if einit.models.User.does_username_exist(form.name.data):
      flask.flash('Username already exists','danger')
      return flask.render_template('signup.html',form=form)

    if einit.models.User.does_email_exist(form.email.data):
      flask.flash('Email already taken','danger')
      return flask.render_template('signup.html',form=form)

    u = einit.models.User.create_user(form.name.data, form.email.data, form.password.data)
    u.save()
    #log in user - give them a session token and flash a welcome
    flask.flash('Account Created - Welcome!','success')
    flask.ext.login.login_user(u, remember=True)

    return flask.redirect(flask.url_for("index"), code=302) #force method to get
  #validation failed, flash errors
  return flask.render_template('signup.html',form=form)

@app.route('/signin', methods=['GET','POST'])
def signin():
  form = einit.views.SignInForm()
  if form.validate_on_submit():
    u = einit.models.User.get_user_by_email(form.name_or_email.data)
    if u and u.check_password(form.password.data):
      flask.flash('%s Signed In'%(u.get_name()), 'success')
      flask.ext.login.login_user(u, remember=True)
      return flask.redirect(flask.request.args.get("next") or flask.url_for("index"))
    #otherwise try logging in by name
    u = einit.models.User.get_user_by_name(form.name_or_email.data)
    if u and u.check_password(form.password.data):
      flask.flash('%s Signed In'%(u.get_name()), 'success')
      flask.ext.login.login_user(u, remember=True)
      return flask.redirect(flask.request.args.get("next") or flask.url_for("index"))
    #Uh Oh, we couldn't log them in
    flask.flash('Invalid username, email or password','danger')
  #validation failed, flash errors
  return flask.render_template('signin.html',form=form)

@app.route("/signout")
@flask.ext.login.login_required
def signout():
    flask.ext.login.logout_user()
    return flask.redirect(flask.url_for("index"))

@app.route("/hero")
@app.route("/home")
@flask.ext.login.login_required
def hero():
  return flask.render_template("hero.html")

@app.route("/hero/create", methods=['GET','POST'])
@flask.ext.login.login_required
def create_hero():
  form = einit.views.HeroForm()
  if form.validate_on_submit():
    h = einit.models.Hero(flask.ext.login.current_user)
    h.hero_name = form.hero_name.data
    h.player_name = form.player_name.data
    h.level = form.level.data
    h.max_hp = form.max_hp.data
    h.initiative_modifier = form.initiative_modifier.data
    h.save()
    flask.flash("Hero created",'success')
    return flask.redirect(flask.url_for("edit_hero",hero_id=h.get_id()))
  return flask.render_template("create_hero.html",form=form)

@app.route("/hero/<int:hero_id>", methods=['GET','PUT','POST'])
@flask.ext.login.login_required
def edit_hero(hero_id):
  form = einit.views.HeroForm()
  hero = flask.ext.login.current_user.get_hero_by_id(hero_id)
  if hero is None:
    flask.flash('Unable to find hero','warning')
    flask.redirect(flask.url_for('index'))
  if form.validate_on_submit():
    hero.hero_name = form.hero_name.data
    hero.player_name = form.player_name.data
    hero.level = form.level.data
    hero.max_hp = form.max_hp.data
    hero.initiative_modifier = form.initiative_modifier.data
    hero.save()
    flask.flash("%s updated"%(hero.hero_name),'success')
  else:
    form.hero_name.data = hero.hero_name
    form.player_name.data = hero.player_name
    form.level.data = hero.level
    form.max_hp.data = hero.max_hp
    form.initiative_modifier.data = hero.initiative_modifier
  return flask.render_template("edit_hero.html",form=form, hero=hero)

@app.route("/hero/<int:hero_id>/destroy", methods=['GET','DELETE'])
@flask.ext.login.login_required
def destroy_hero(hero_id):
  hero = flask.ext.login.current_user.get_hero_by_id(hero_id)
  if hero is None:
    flask.flash("Could not find hero",'warning')
  else:
    flask.flash("%s Deleted forever"%(hero.hero_name),'danger')
    hero.destroy()
  return flask.redirect(flask.url_for('hero'))

@app.route("/monster")
@flask.ext.login.login_required
def monster():
  return flask.render_template("monster.html")

@app.route("/monster/create", methods=['GET','POST'])
@flask.ext.login.login_required
def create_monster():
  form = einit.views.MonsterForm()
  if form.validate_on_submit():
    m = einit.models.Monster(flask.ext.login.current_user)
    m.name = form.name.data
    m.level = form.level.data
    m.second_role = form.second_role.data
    m.origin = form.origin.data
    m.monster_type = form.monster_type.data
    m.keywords = form.keywords.data
    m.max_hp = form.max_hp.data
    m.initiative_modifier = form.initiative_modifier.data
    m.ac = form.ac.data
    m.fortitude = form.fortitude.data
    m.reflex = form.reflex.data
    m.will = form.will.data
    m.perception = form.perception.data
    m.senses = form.senses.data
    m.speed = form.speed.data
    m.immune = form.immune.data
    m.resist = form.resist.data
    m.vulnerable = form.vulnerable.data
    m.saving_throws = form.saving_throws.data
    m.action_points = form.action_points.data
    m.save()
    flask.flash("Monster created",'success')
    return flask.redirect(flask.url_for("view_monster",monster_id=m.get_id()))
  return flask.render_template("create_monster.html",form=form)

@app.route("/monster/create_file", methods=['GET','POST'])
@flask.ext.login.login_required
def create_monster_file():
  form = einit.views.XmlMonsterForm()
  if form.validate_on_submit():
    try:
      m = einit.models.Monster(flask.ext.login.current_user)
      einit.models.monster_from_xml(
        flask.request.files['filename'].read(),
        m)
      flask.flash("Monster Created","success")
      return flask.redirect(flask.url_for('view_monster',monster_id=m.get_id()))
    except:
      if app.config['DEBUG']==True:
        raise
      flask.flash("Error processing monster file","danger")
  return flask.render_template("create_monster_file.html", form=form)

@app.route("/monster/<int:monster_id>", methods=['GET'])
@flask.ext.login.login_required
def view_monster(monster_id):
  m = flask.ext.login.current_user.get_monster_by_id(monster_id)
  if m is None:
    flask.flash('Unable to find monster','warning')
    return flask.redirect(flask.url_for('index'))
  return flask.render_template("view_monster.html",monster=m)

@app.route("/monster/<int:monster_id>/edit", methods=['GET','PUT','POST'])
@flask.ext.login.login_required
def edit_monster(monster_id):
  form = einit.views.MonsterForm()
  m = flask.ext.login.current_user.get_monster_by_id(monster_id)
  if m is None:
    flask.flash('Unable to find monster','warning')
    return sflask.redirect(flask.url_for('index'))
  if form.validate_on_submit():
    m.name = form.name.data
    m.level = form.level.data
    m.second_role = form.second_role.data
    m.origin = form.origin.data
    m.monster_type = form.monster_type.data
    m.keywords = form.keywords.data
    m.max_hp = form.max_hp.data
    m.initiative_modifier = form.initiative_modifier.data
    m.ac = form.ac.data
    m.fortitude = form.fortitude.data
    m.reflex = form.reflex.data
    m.will = form.will.data
    m.perception = form.perception.data
    m.senses = form.senses.data
    m.speed = form.speed.data
    m.immune = form.immune.data
    m.resist = form.resist.data
    m.vulnerable = form.vulnerable.data
    m.saving_throws = form.saving_throws.data
    m.action_points = form.action_points.data
    m.save()
    flask.flash("%s updated"%(m.name),'success')
  else:
    form.name.data = m.name
    form.level.data = m.level
    form.second_role.data = m.second_role
    form.origin.data = m.origin
    form.monster_type.data = m.monster_type
    form.keywords.data = m.keywords
    form.max_hp.data = m.max_hp
    form.initiative_modifier.data = m.initiative_modifier
    form.ac.data = m.ac
    form.fortitude.data = m.fortitude
    form.reflex.data = m.reflex
    form.will.data = m.will
    form.perception.data = m.perception
    form.senses.data = m.senses
    form.speed.data = m.speed
    form.immune.data = m.immune
    form.resist.data = m.resist
    form.vulnerable.data = m.vulnerable
    form.saving_throws.data = m.saving_throws
    form.action_points.data = m.action_points
  return flask.render_template("edit_monster.html",form=form, monster=m)

@app.route("/monster/<int:monster_id>/destroy", methods=['GET','DELETE'])
@flask.ext.login.login_required
def destroy_monster(monster_id):
  monster = flask.ext.login.current_user.get_monster_by_id(monster_id)
  if monster is None:
    flask.flash("Could not find monster",'warning')
  else:
    flask.flash("%s Deleted forever"%(monster.name),'danger')
    monster.destroy()
  return flask.redirect(flask.url_for('monster'))

@app.route("/monster/<int:monster_id>/action/create",methods=['GET','POST'])
@flask.ext.login.login_required
def create_monster_action(monster_id):
  form = einit.views.MonsterActionForm()
  monster = flask.ext.login.current_user.get_monster_by_id(monster_id)
  if monster is None:
    flask.flash("Could not find monster","warning")
    return flask.redirect(flask.url_for('monster'))
  if form.validate_on_submit():
    ma = einit.models.MonsterAction(monster)
    ma.category = form.category.data
    ma.aura_range = form.aura_range.data
    ma.recharge = form.recharge.data
    ma.frequency = form.frequency.data
    ma.icon = form.icon.data
    ma.name = form.name.data
    ma.description = form.description.data
    ma.trigger = form.trigger.data
    ma.trigger_usage = form.trigger_usage.data    
    ma.attack = form.attack.data
    ma.hit = form.hit.data
    ma.miss = form.miss.data
    ma.effect = form.effect.data
    ma.secondary_attack = form.secondary_attack.data
    ma.aftereffect = form.aftereffect.data
    ma.special = form.special.data
    ma.keywords = form.keywords.data
    ma.save()
    flask.flash("Monster action created",'success')
    return flask.redirect(flask.url_for("view_monster",monster_id=monster_id))
  return flask.render_template("create_monster_action.html",form=form, monster=monster)

@app.route("/monster/<int:monster_id>/action/<int:action_id>")
@flask.ext.login.login_required
def view_monster_action(monster_id, action_id):
  return flask.redirect(flask.url_for('view_monster',monster_id=monster_id))

@app.route("/monster/<int:monster_id>/action/<int:action_id>/edit",methods=['GET','POST','PUT'])
@flask.ext.login.login_required
def edit_monster_action(monster_id, action_id):
  form = einit.views.MonsterActionForm()
  monster = flask.ext.login.current_user.get_monster_by_id(monster_id)
  if monster is None:
    flask.flash("Could not find monster","warning")
    return flask.redirect(flask.url_for('monster'))
  ma = monster.get_action_by_id(action_id)
  if ma is None:
    flask.flash("Could not find monster action",'warning')
    return flask.redirect(flask.url_for('view_monster',monster_id=monster_id))
  if form.validate_on_submit():
    ma.category = form.category.data
    ma.aura_range = form.aura_range.data
    ma.recharge = form.recharge.data
    ma.frequency = form.frequency.data
    ma.icon = form.icon.data
    ma.name = form.name.data
    ma.description = form.description.data
    ma.trigger = form.trigger.data
    ma.trigger_usage = form.trigger_usage.data
    ma.attack = form.attack.data
    ma.hit = form.hit.data
    ma.miss = form.miss.data
    ma.effect = form.effect.data
    ma.secondary_attack = form.secondary_attack.data
    ma.aftereffect = form.aftereffect.data
    ma.special = form.special.data
    ma.keywords = form.keywords.data
    ma.save()
    flask.flash("Monster action updated",'success')
    return flask.redirect(flask.url_for("view_monster",monster_id=monster.get_id()))
  else:
    form.category.data = ma.category
    form.aura_range.data = ma.aura_range
    form.recharge.data = ma.recharge
    form.frequency.data = ma.frequency
    form.icon.data = ma.icon
    form.name.data = ma.name
    form.description.data = ma.description
    form.trigger.data = ma.trigger
    form.trigger_usage.data = ma.trigger_usage
    form.attack.data = ma.attack
    form.hit.data = ma.hit
    form.miss.data = ma.miss
    form.effect.data = ma.effect
    form.secondary_attack.data = ma.secondary_attack
    form.aftereffect.data = ma.aftereffect
    form.special.data = ma.special
    form.keywords.data = ma.keywords
  return flask.render_template("edit_monster_action.html",form=form, monster=monster, action=ma)

@app.route("/monster/<int:monster_id>/action/<int:action_id>/destroy", methods=['GET','DELETE'])
@flask.ext.login.login_required
def destroy_monster_action(monster_id, action_id):
  monster = flask.ext.login.current_user.get_monster_by_id(monster_id)
  if monster is None:
    flask.flash("Could not find monster",'warning')
    return flask.redirect(flask.url_for('monster'))
  else:
    action = monster.get_action_by_id(action_id)
    if action is None:
      flask.flash("Could not find action", 'warning')
    else:
      flask.flash("%s Deleted forever"%(action.name),'danger')
      action.destroy()
  return flask.redirect(flask.url_for('view_monster',monster_id=monster_id))


##encounter routes
@app.route("/encounter",methods=['GET'])
@flask.ext.login.login_required
def encounter():
  return flask.render_template("encounter.html")

@app.route("/encounter/create",methods=['GET','POST'])
@flask.ext.login.login_required
def create_encounter():
  form = einit.views.EncounterForm()
  if form.validate_on_submit():
    m = einit.models.Encounter(flask.ext.login.current_user)
    m.name = form.name.data
    m.description = form.description.data
    m.save()
    flask.flash("Encounter created",'success')
    return flask.redirect(flask.url_for("view_encounter",encounter_id=m.get_id()))
  return flask.render_template("create_encounter.html",form=form)


@app.route("/encounter/<int:encounter_id>", methods=['GET'])
@flask.ext.login.login_required
def view_encounter(encounter_id):
  e = flask.ext.login.current_user.get_encounter_by_id(encounter_id)
  if e is None:
    flask.flash('Unable to find encounter','warning')
    return flask.redirect(flask.url_for('index'))
  return flask.render_template("view_encounter.html",encounter=e)


@app.route("/encounter/<int:encounter_id>/edit", methods=['GET','PUT','PATCH','POST'])
@flask.ext.login.login_required
def edit_encounter(encounter_id):
  form = einit.views.EncounterForm()
  encounter = flask.ext.login.current_user.get_encounter_by_id(encounter_id)
  if hero is None:
    flask.flash('Unable to find encounter','warning')
    flask.redirect(flask.url_for('index'))
  if form.validate_on_submit():
    encounter.name = form.name.data
    encounter.description = form.description.data
    encounter.save()
    flask.flash("%s updated"%(encounter.name),'success')
  else:
    form.name.data = encounter.name
    form.description.data = encounter.description
  return flask.render_template("edit_encounter.html",form=form, encounter=encounter)

@app.route("/encounter/<int:encounter_id>/destroy", methods=['GET','DELETE'])
@flask.ext.login.login_required
def destroy_encounter(encounter_id):
  e = flask.ext.login.current_user.get_encounter_by_id(encounter_id)
  if e is None:
    flask.flash('Unable to find encounter','warning')
    return flask.redirect(flask.url_for('index'))
  flask.flash('Encounter %s deleted forever'%(e.name),'danger')
  e.destroy()
  return flask.render_template("encounter.html")

@app.route("/encounter/<int:encounter_id>/hero",methods=['GET'])
@flask.ext.login.login_required
def encounter_hero_list(encounter_id):
  e = flask.ext.login.current_user.get_encounter_by_id(encounter_id)
  if e is None:
    flask.flash("Unable to find encounter",'warning')
    return flask.redirect(flask.url_for('index'))
  encounter_heroes = e.get_heroes()
  available_heroes = filter(lambda h: h.get_id() not in map(lambda x: x.get_id(),encounter_heroes), flask.ext.login.current_user.get_heroes())
  return flask.render_template("view_actor_list.html",
    available_actors=available_heroes,
    encounter_actors=encounter_heroes,
    encounter=e,
    add_callback='encounter_hero_add',
    del_callback='encounter_hero_del'
    )

@app.route('/encounter/<int:encounter_id>/hero/add/<int:actor_id>', methods=['GET','POST'])
@flask.ext.login.login_required
def encounter_hero_add(encounter_id, actor_id):
  hero = flask.ext.login.current_user.get_hero_by_id(actor_id)
  if hero is None:
    flask.flash("Unable to find hero",'warning')
    return flask.redirect(flask.url_for('encounter_hero_list',encounter_id=encounter_id))
  encounter = flask.ext.login.current_user.get_encounter_by_id(encounter_id)
  if encounter is None:
    flask.flash("Unable to find encounter",'warning')
    return flask.redirect(flask.url_for('index'))
  encounter.add_hero(hero)
  flask.flash("Added %s"%hero.hero_name,'success')
  return flask.redirect(flask.url_for('encounter_hero_list',encounter_id=encounter_id))

@app.route('/encounter/<int:encounter_id>/hero/del/<int:actor_id>', methods=['GET','POST'])
@flask.ext.login.login_required
def encounter_hero_del(encounter_id, actor_id):
  hero = flask.ext.login.current_user.get_hero_by_id(actor_id)
  if hero is None:
    flask.flash("Unable to find hero",'warning')
    return flask.redirect(flask.url_for('encounter_hero_list',encounter_id=encounter_id))
  encounter = flask.ext.login.current_user.get_encounter_by_id(encounter_id)
  if encounter is None:
    flask.flash("Unable to find encounter",'warning')
    return flask.redirect(flask.url_for('index'))
  encounter.remove_hero(hero)
  flask.flash("Removed %s"%hero.hero_name,"danger")
  return flask.redirect(flask.url_for('encounter_hero_list',encounter_id=encounter_id))

@app.route("/encounter/<int:encounter_id>/monster",methods=['GET'])
@flask.ext.login.login_required
def encounter_monster_list(encounter_id):
  e = flask.ext.login.current_user.get_encounter_by_id(encounter_id)
  if e is None:
    flask.flash("Unable to find encounter",'warning')
    return flask.redirect(flask.url_for('index'))
  encounter_monsters = e.get_monsters()
  available_monsters = flask.ext.login.current_user.get_monsters()
  return flask.render_template("view_actor_list.html",
    available_actors=available_monsters,
    encounter_actors=encounter_monsters,
    encounter=e,
    add_callback='encounter_monster_add',
    del_callback='encounter_monster_del'
    )

@app.route('/encounter/<int:encounter_id>/monster/add/<int:actor_id>', methods=['GET','POST'])
@flask.ext.login.login_required
def encounter_monster_add(encounter_id, actor_id):
  monster = flask.ext.login.current_user.get_monster_by_id(actor_id)
  if monster is None:
    flask.flash("Unable to find monster",'warning')
    return flask.redirect(flask.url_for('encounter_monster_list',encounter_id=encounter_id))
  encounter = flask.ext.login.current_user.get_encounter_by_id(encounter_id)
  if encounter is None:
    flask.flash("Unable to find encounter",'warning')
    return flask.redirect(flask.url_for('index'))
  encounter.add_monster(monster)
  flask.flash("Added %s"%monster.name,'success')
  return flask.redirect(flask.url_for('encounter_monster_list',encounter_id=encounter_id))

@app.route('/encounter/<int:encounter_id>/monster/del/<int:actor_id>', methods=['GET','POST'])
@flask.ext.login.login_required
def encounter_monster_del(encounter_id, actor_id):
  monster = flask.ext.login.current_user.get_monster_by_id(actor_id)
  if monster is None:
    flask.flash("Unable to find monster",'warning')
    return flask.redirect(flask.url_for('encounter_monster_list',encounter_id=encounter_id))
  encounter = flask.ext.login.current_user.get_encounter_by_id(encounter_id)
  if encounter is None:
    flask.flash("Unable to find encounter",'warning')
    return flask.redirect(flask.url_for('index'))
  encounter.remove_actor(monster)
  flask.flash("Removed %s"%monster.name,"danger")
  return flask.redirect(flask.url_for('encounter_monster_list',encounter_id=encounter_id))

@app.route('/encounter/<int:encounter_id>/event',methods=['GET'])
@flask.ext.login.login_required
def encounter_event_list(encounter_id):
  encounter = flask.ext.login.current_user.get_encounter_by_id(encounter_id)
  if encounter is None:
    flask.flash("Unable to find encounter","warning")
    return flask.redirect(flask.url_for('index'))
  event_form = einit.views.EncounterEventForm()
  return flask.render_template("view_encounter_event_list.html",encounter=encounter, event_form=event_form)

@app.route('/encounter/<int:encounter_id>/event/add',methods=['GET','POST'])
@flask.ext.login.login_required
def encounter_event_add(encounter_id):
  encounter = flask.ext.login.current_user.get_encounter_by_id(encounter_id)
  if encounter is None:
    flask.flash("Unable to find encounter","warning")
    return flask.redirect(flask.url_for('index'))
  form = einit.views.EncounterEventForm()
  if form.validate_on_submit():
    flask.flash("%s event added",form.name.data)
    encounter.add_event(form.name.data, form.description.data)
  return flask.redirect(flask.url_for('encounter_event_list',encounter_id=encounter.get_id()))

@app.route('/encounter/<int:encounter_id>/event/<int:event_id>/destroy',methods=['GET','DELETE'])
@flask.ext.login.login_required
def encounter_event_del(encounter_id, event_id):
  encounter = flask.ext.login.current_user.get_encounter_by_id(encounter_id)
  if encounter is None:
    flask.flash("Unable to find encounter","warning")
    return flask.redirect(flask.url_for('index'))
  event = encounter.get_event_by_id(event_id)
  if event is None:
    flask.flash("Unable to find event","warning")
  else:
    flask.flash("%s event deleted forever"%event.name, 'danger')
    event.destroy()
  return flask.redirect(flask.url_for('encounter_event_list',encounter_id=encounter_id))

@app.route("/encounter/<int:encounter_id>/start", methods=['GET',"POST"])
@flask.ext.login.login_required
def start_encounter(encounter_id):
  encounter = flask.ext.login.current_user.get_encounter_by_id(encounter_id)
  if encounter is None:
    flask.flash("Unable to find encounter","warning")
    return flask.redirect(flask.url_for('index'))
  form = einit.views.EncounterStartForm()
  if form.validate_on_submit():
    events = []
    while len(form.actors) > 0:
      f = form.actors.pop_entry()
      actor = encounter.get_actor_by_category_id(f.actor_category.data, f.actor_id.data)
      if actor is None:
        flask.flash("Could not find actor")
        return flask.redirect(flask.url_for('index'))
      for i in range(0,encounter.get_actor_spawn_count(actor)):
        e = einit.models.EncounterEntry(encounter)
        e.initiative = abs(f.initiative.data)
        e.spawn_index = i
        e.hp = f.starting_hp.data
        e.temp_hp = 0
        e.visible = (f.initiative.data >= 0) #negative initiative means entry is initially hidden
        e.category = f.actor_category.data
        e.reference_id = f.actor_id.data
        events.append(e)
    while len(form.events) > 0:
      f = form.events.pop_entry()
      e.initiative = abs(f.initiative.data)
      e.spawn_index = 0
      e.hp = 0
      e.temp_hp = 0
      e.visible = (f.initiative.data >= 0)
      e.category = 'event'
      e.reference_id = f.event_id.data
      events.append(e)
    encounter.start(events)
    return flask.redirect(flask.url_for('manage_encounter',encounter_id=encounter_id))
  else:
    while len(form.actors) > 0:
      form.actors.pop_entry()
    for actor in encounter.get_heroes():
      form.actors.append_entry()
      form.actors[-1].actor_category.data = actor.get_category()
      form.actors[-1].actor_id.data = actor.get_id()
      form.actors[-1].starting_hp.data = actor.get_max_hp()
      form.actors[-1].initiative.data = random.choice(range(1,20))+actor.get_initiative_modifier()
    for actor in encounter.get_monsters():
      form.actors.append_entry()
      form.actors[-1].actor_category.data = actor.get_category()
      form.actors[-1].actor_id.data = actor.get_id()
      form.actors[-1].starting_hp.data = actor.get_max_hp()
      form.actors[-1].initiative.data = random.choice(range(1,20))+actor.get_initiative_modifier()
    while len(form.events) > 0:
      form.events.pop_entry()
    for event in encounter.get_events():
      form.events.append_entry()
      form.events[-1].event_id.data = event.get_id()
      form.events[-1].initiative.data = 0
  return flask.render_template("start_encounter.html",encounter=encounter, form=form)
  
@app.route("/encounter/<int:encounter_id>/abandon", methods=['GET','DELETE'])
@flask.ext.login.login_required
def abandon_encounter(encounter_id):
  encounter = flask.ext.login.current_user.get_encounter_by_id(encounter_id)
  if encounter is None:
    flask.flash("Unable to find encounter","warning")
    return flask.redirect(flask.url_for('index'))
  encounter.abandon()
  redis.publish(encounter.get_encounter_hash_key(),'abandon')
  return flask.redirect(flask.url_for("view_encounter",encounter_id=encounter_id))
 
@app.route("/encounter/<int:encounter_id>/manage", methods=['GET',"POST"], defaults={'active_entry_id':0})
@app.route("/encounter/<int:encounter_id>/manage/entry/<int:active_entry_id>", methods=['GET',"POST"])
@flask.ext.login.login_required
def manage_encounter(encounter_id, active_entry_id):
  encounter = flask.ext.login.current_user.get_encounter_by_id(encounter_id)
  if encounter is None:
    flask.flash("Unable to find encounter","warning")
    return flask.redirect(flask.url_for('index'))
  if encounter.round == 0:
    flask.flash("Encounter not in progress","warning")
    return flask.redirect(flask.url_for('view_encounter',encounter_id=encounter_id))
  return flask.render_template("manage_encounter.html",encounter=encounter, active_entry_id=active_entry_id,hp_form=einit.views.ModifyHitPointsForm())

@app.route("/encounter/<int:encounter_id>/entry/<int:round>/<int:entry_id>", methods=['GET','PUT','POST','PATCH'])
@flask.ext.login.login_required
def goto_entry(encounter_id, round, entry_id):
  encounter = flask.ext.login.current_user.get_encounter_by_id(encounter_id)
  if encounter is None:
    flask.flash("Unable to find encounter","warning")
    return flask.redirect(flask.url_for('index'))
  if encounter.round == 0:
    flask.flash("Encounter not in progress","warning")
    return flask.redirect(flask.url_for('view_encounter',encounter_id=encounter_id))
  encounter.set_current_event(round, entry_id)
  redis.publish(encounter.get_encounter_hash_key(),'move')
  return flask.redirect(flask.url_for('manage_encounter',encounter_id=encounter_id))

@app.route("/encounter/<int:encounter_id>/manage/entry/<int:entry_id>/make_visible", methods=['GET','POST','PUT','PATCH'])
@flask.ext.login.login_required
def make_visible(encounter_id, entry_id):
  return set_visibility(encounter_id, entry_id, True)

@app.route("/encounter/<int:encounter_id>/manage/entry/<int:entry_id>/make_invisible", methods=['GET','POST','PUT','PATCH'])
@flask.ext.login.login_required
def make_invisible(encounter_id, entry_id):
  return set_visibility(encounter_id, entry_id, False)

def set_visibility(encounter_id, entry_id, visibility):
  encounter = flask.ext.login.current_user.get_encounter_by_id(encounter_id)
  if encounter is None:
    flask.flash("Unable to find encounter","warning")
    return flask.redirect(flask.url_for('index'))
  if encounter.round == 0:
    flask.flash("Encounter not in progress","warning")
    return flask.redirect(flask.url_for('view_encounter',encounter_id=encounter_id))
  entry = encounter.get_entry_by_id(entry_id)
  if entry is None:
    flask.flash("unable to find entry","warning")
    return flask.redirect(flask.url_for('manage_encounter',encounter_id=encounter_id))
  entry.visible = visibility
  entry.save()
  redis.publish(encounter.get_encounter_hash_key(),'visibility')
  return flask.redirect(flask.url_for('manage_encounter',encounter_id=encounter_id,active_entry_id=entry_id))

@app.route("/encounter/<int:encounter_id>/manage/entry/<int:entry_id>/spawn", methods=['GET','POST','PUT','PATCH'])
@flask.ext.login.login_required
def spawn_monster(encounter_id, entry_id):
  encounter = flask.ext.login.current_user.get_encounter_by_id(encounter_id)
  if encounter is None:
    flask.flash("Unable to find encounter","warning")
    return flask.redirect(flask.url_for('index'))
  if encounter.round == 0:
    flask.flash("Encounter not in progress","warning")
    return flask.redirect(flask.url_for('view_encounter',encounter_id=encounter_id))
  entry = encounter.get_entry_by_id(entry_id)
  if entry is None:
    flask.flash("unable to find entry","warning")
    return flask.redirect(flask.url_for('manage_encounter',encounter_id=encounter_id))
  if entry.category != "monster":
    flask.flash("Can only spawn monsters","warning")
    return flask.redirect(flask.url_for('manage_encounter',encounter_id=encounter_id, active_entry_id=entry_id))
  monster = encounter.get_actor_by_category_id(entry.category,entry.reference_id)
  encounter.spawn_monster(monster)
  redis.publish(encounter.get_encounter_hash_key(),'spawn')
  return flask.redirect(flask.url_for('manage_encounter',encounter_id=encounter_id, active_entry_id=entry_id))
    
@app.route("/encounter/<int:encounter_id>/manage/entry/<int:entry_id>/modify_hp",methods=['POST','PUT','GET'])
@flask.ext.login.login_required
def mod_hp(encounter_id, entry_id):
  encounter = flask.ext.login.current_user.get_encounter_by_id(encounter_id)
  if encounter is None:
    flask.flash("Unable to find encounter","warning")
    return flask.redirect(flask.url_for('index'))
  if encounter.round == 0:
    flask.flash("Encounter not in progress","warning")
    return flask.redirect(flask.url_for('view_encounter',encounter_id=encounter_id))
  entry = encounter.get_entry_by_id(entry_id)
  if entry is None:
    flask.flash("unable to find entry","warning")
    return flask.redirect(flask.url_for('manage_encounter',encounter_id=encounter_id))
  hp_form = einit.views.ModifyHitPointsForm()
  if hp_form.validate_on_submit():
    if hp_form.action.data=='damage':
      entry.apply_damage(hp_form.amount.data)
    elif hp_form.action.data=='temp_hp':
      entry.apply_temp_hp(hp_form.amount.data)
    elif hp_form.action.data=='heal':
      entry.apply_heal(hp_form.amount.data)
    entry.save()
    redis.publish(encounter.get_encounter_hash_key(),'hp')
  else:
    for fieldname, error_list in hp_form.errors:
      for error in error_list:
        flask.flash("%s: %s"%(fieldname, error),"warning")
  return flask.redirect(flask.url_for('manage_encounter',encounter_id=encounter_id, active_entry_id=entry_id))

@app.route("/encounter/<int:encounter_id>/manage/entry/<int:entry_id>/clear_status/<string:status_str>",methods=['POST','PUT','GET','DELETE'])
@flask.ext.login.login_required
def clear_status(encounter_id, entry_id, status_str):
  return status_action(encounter_id, entry_id, status_str, einit.models.EncounterEntry.clear_status)

@app.route("/encounter/<int:encounter_id>/manage/entry/<int:entry_id>/set_status/<string:status_str>",methods=['POST','PUT','GET'])
@flask.ext.login.login_required
def set_status(encounter_id, entry_id, status_str):
  return status_action(encounter_id, entry_id, status_str, einit.models.EncounterEntry.set_status)

def status_action(encounter_id, entry_id, status_str, status_functor):
  encounter = flask.ext.login.current_user.get_encounter_by_id(encounter_id)
  if encounter is None:
    flask.flash("Unable to find encounter","warning")
    return flask.redirect(flask.url_for('index'))
  if encounter.round == 0:
    flask.flash("Encounter not in progress","warning")
    return flask.redirect(flask.url_for('view_encounter',encounter_id=encounter_id))
  entry = encounter.get_entry_by_id(entry_id)
  if entry is None:
    flask.flash("unable to find entry","warning")
    return flask.redirect(flask.url_for('manage_encounter',encounter_id=encounter_id))
  status_functor(entry, status_str)
  entry.save()
  redis.publish(encounter.get_encounter_hash_key(),'status')
  return flask.redirect(flask.url_for('manage_encounter',encounter_id=encounter_id, active_entry_id=entry_id))

@app.route("/observe/<string:encounter_hash_key>", methods=["GET"])
def encounter_app(encounter_hash_key):
  encounter = models.Encounter.get_encounter_by_hash(encounter_hash_key)
  if encounter is None:
    flask.flash("Unable to find encounter","warning")
    return flask.redirect(flask.url_for('index'))
  encounter_id = encounter.get_id()
  if encounter.round == 0:
    flask.flash("Encounter not in progress","warning")
    return flask.redirect(flask.url_for('view_encounter',encounter_id=encounter_id))
  return flask.render_template('encounter_app.html',encounter=encounter)

@app.route("/observe/<string:encounter_hash_key>.json")
def encounter_json(encounter_hash_key):
  encounter = models.Encounter.get_encounter_by_hash(encounter_hash_key)
  if encounter is None:
    flask.flash("Unable to find encounter","warning")
    return flask.Response(response=flask.render_template("error_json.json"),mimetype="application/json")
  return flask.json.jsonify(views.render_encounter_as_dict(encounter))

def event_stream(key):
  pubsub = redis.pubsub()
  pubsub.subscribe(key)
  for message in pubsub.listen():
    yield 'data: %s\n\n'%message['data']

@app.route("/observe/<string:encounter_hash_key>/subscribe")
def encounter_subscribe(encounter_hash_key):
  return flask.Response(event_stream(encounter_hash_key),mimetype="text/event-stream")