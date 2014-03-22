import flask

app = flask.Flask(__name__)

#register routes
@app.route('/')
@app.route('/index')
def index():
  return "Einit"
