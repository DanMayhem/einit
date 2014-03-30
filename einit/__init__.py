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
app.config['SQLALCHEMY_MIGRATE_REPO'] = os.path.join(os.path.abspath(os.path.split(os.path.dirname(__file__))[0]),'migrations')
db = flask.ext.sqlalchemy.SQLAlchemy(app)

#load secure token
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

#other flask extensions
sslify = flask_sslify.SSLify(app) #requires SSL
bcrypt = flaskext.bcrypt.Bcrypt(app) #password digests
bootstrap = flask_bootstrap.Bootstrap(app) #make bootstrap templates and helpers available.
login_manager = flask.ext.login.LoginManager(app) #login manager
login_manager.login_view = "signin"
login_manager.login_message_category = 'warning'

#import models, views and helpers
import einit.models
import einit.views
import einit.user_support

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




