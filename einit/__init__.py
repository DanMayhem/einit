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

#import models, views and helpers
import einit.models
import einit.views
import einit.user_support

#register static routes
@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
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

    u = einit.models.User(form.name.data, form.email.data, form.password.data)
    u.save()
    #log in user - give them a session token and flash a welcome
    flask.flash('Account Created - Welcome!','success')
    flask.ext.login.login_user(u, remember=True)

    return flask.redirect(flask.url_for("index"), code=302) #force method to get
  #validation failed, flash errors
  return flask.render_template('signup.html',form=form)
