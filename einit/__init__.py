import flask

app = flask.Flask(__name__)

#set debug mode as appropriate
#load database
#load secure token

#register routes
@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
  return flask.render_template("index.html")
