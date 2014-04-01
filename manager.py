#!python
import flask

import flask.ext.script
import flask.ext.migrate

import einit

if __name__=='__main__':
  migrate = flask.ext.migrate.Migrate(einit.app, einit.db)
  manager = flask.ext.script.Manager(einit.app)
  manager.add_command('db',flask.ext.migrate.MigrateCommand)
  manager.run()
