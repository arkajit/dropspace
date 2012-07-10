# Credits: inspired by https://github.com/jamesward/flaskbars.

from flaskext.script import Manager
from app import db, app

manager = Manager(app)

@manager.command
def createDB():
  db.create_all() 
