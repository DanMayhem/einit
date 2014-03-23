import os

import redis
import Crypto.Random
import base64

import flask
import flask.ext.sqlalchemy
import flask_sslify
import flaskext.bcrypt

app = flask.Flask(__name__)

#set debug mode as appropriate
if os.environ.has_key("DEBUG_EINIT"):
  app.debug=True

#load databases
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL',"sqllite://")
app.config['SQLALCHEMY_MIGRATE_REPO'] = os.path.join(os.path.abspath(os.path.split(os.path.dirname(__file__))[0]),'migrations')
db = flask.ext.sqlalchemy.SQLAlchemy(app)
redis = redis.from_url(os.environ.get('REDISTOGO_URL'))

#load secure token
if not redis.exists('secret'):
  #add secret key to redis DB
  redis.set('secret_key',base64.b64encode(Crypto.Random.get_random_bytes(16)))
app.config['SECRET_KEY'] = redis.get('secret_key')

#require SSL unless in debug mode
sslify = flask_sslify.SSLify(app)

#import models, views and helpers
import einit.models

#register routes
@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
  return flask.render_template("index.html")
