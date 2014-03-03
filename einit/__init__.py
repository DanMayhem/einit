#import os
import flask

app = flask.Flask(__name__)

@app.route('/')
def hello():
    return flask.render_template('index.html')

