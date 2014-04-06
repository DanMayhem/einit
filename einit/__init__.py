import os

import flask
import flask.ext.sqlalchemy
import flask.ext.login
import flask_bootstrap
import flask_sslify
import flaskext.bcrypt

import Crypto.Random
import base64
import hashlib


app = flask.Flask(__name__)

#set debug mode and other config options as appropriate
if os.environ.has_key("DEBUG_EINIT"):
  app.debug=True
app.config['CSRF_ENABLED'] = True

#load databases
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL',"sqllite://")
#app.config['SQLALCHEMY_MIGRATE_REPO'] = os.path.join(os.path.abspath(os.path.split(os.path.dirname(__file__))[0]),'migrations')
db = flask.ext.sqlalchemy.SQLAlchemy(app)

#load secure token
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

#other flask extensions
sslify = flask_sslify.SSLify(app) #requires SSL
bcrypt = flaskext.bcrypt.Bcrypt(app) #password digests
bootstrap = flask_bootstrap.Bootstrap(app) #make bootstrap templates and helpers available.
login_manager = flask.ext.login.LoginManager(app) #login manager

#import models, views and helpers
import einit.models
import einit.views
import einit.user_support
import einit.xml_support

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
      einit.xml_support.monster_from_xml(
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












