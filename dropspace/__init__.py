import dropbox
import flask

from creds import APP_KEY, APP_SECRET, ACCESS_TYPE
from flask.ext.sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)
app.secret_key = '\x9de\xbe\x8d\xfc\xacw\xc1\xefhO\x8dm\xbd\xc9\xb9i\xbb\x99}\xf9\xd1k\x17'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

session = dropbox.session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
client = dropbox.client.DropboxClient(session)

# These imports must be at the end since the following modules depend on the
# objects created above. (This is a bit circular, but is actually the structure
# recommended here: http://flask.pocoo.org/docs/patterns/packages/).
import dropspace.views
import dropspace.ajax_views
import dropspace.filters
import dropspace.models
