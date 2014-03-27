import os

import flask
import flask.ext.sqlalchemy
import flask_sslify
import flaskext.bcrypt
import flask_bootstrap

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

#import models, views and helpers
import einit.models
import einit.views

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
    if len(db.session.query(einit.models.User).filter(einit.models.User.name == form.name.data).all()) > 0:
      flask.flash('Username already exists','danger')
      return flask.render_template('signup.html',form=form)

    if len(db.session.query(einit.models.User).filter(einit.models.User.email == form.email.data.lower()).all()) > 0:
      flask.flash('Email already taken','danger')
      return flask.render_template('signup.html',form=form)

    u = einit.models.User(form.name.data, form.email.data, form.password.data)
    db.session.add(u)
    db.session.commit()
    #log in user - give them a session token and flash a welcome
    flask.flash('Account Created - Welcome!','success')

    return flask.redirect(flask.url_for("index"), code=302) #force method to get
  #validation failed, flash errors
  return flask.render_template('signup.html',form=form)
