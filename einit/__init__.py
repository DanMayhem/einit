import os

import flask
import flask.ext.sqlalchemy
import flask_sslify
import flaskext.bcrypt

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
@app.route('/signup_form', methods=['GET','POST'])
def signup_form():
  return flask.render_template("signup.html",form=einit.views.SignUpForm())

@app.route('/signup', methods=['POST'])
def create_user():
  form = einit.views.SignUpForm()
  if form.validate_on_submit():
    #check to see if usename exists:
    if db.session.query(einit.models.User).filter(einit.User.name == form.name.data).all >0:
      flask.flash('Username already exists','danger')
      return flask.redirect(flask.url_for("signup_form"))

    u = einit.models.User(form.name.data, form.email.data, form.password.data)
    db.session.add(u)
    db.session.commit()
    return flask.redirect(flask.url_for("index"), code=302) #force method to get
  #validation failed, flash errors
  for k in form.errors:
      for msg in form.errors[k]:
        flask.flash(msg,'danger')
  return flask.redirect(flask.url_for("signup_form"))







