import os
import flask
import flask.ext.sqlalchemy
import flask_sslify

app = flask.Flask(__name__)

#set debug mode as appropriate
if os.environ.has_key("DEBUG_EINIT"):
  app.debug=True

#load database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL',"sqllite://")
app.config['SQLALCHEMY_MIGRATE_REPO'] = os.path.join(os.path.abspath(os.path.split(os.path.dirname(__file__))[0]),'migrations')
db = flask.ext.sqlalchemy.SQLAlchemy(app)
#load secure token

#require SSL unless in debug mode
sslify = flask_sslify.SSLify(app)

#register routes
@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
  return flask.render_template("index.html")
