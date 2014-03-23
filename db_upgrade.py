#!flask/bin/python
from migrate.versioning import api
import os
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',"sqllite://")
SQLALCHEMY_MIGRATE_REPO = os.path.join(os.path.abspath(os.path.dirname(__file__)),'migrations')
api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
print 'Current database version: ' + str(api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO))