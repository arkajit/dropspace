import dropbox
import flask

from creds import APP_KEY, APP_SECRET, ACCESS_TYPE
from flask.ext.sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)
session = dropbox.session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
client = dropbox.client.DropboxClient(session)
COOKIE_NAME = 'dropspace'

# These imports must be at the end since the following modules depend on the
# objects created above. (This is a bit circular, but is actually the structure
# recommended here: http://flask.pocoo.org/docs/patterns/packages/).
import dropspace.views
import dropspace.ajax_views
import dropspace.filters
import dropspace.models
