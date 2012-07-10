import dropbox
import flask
import oauth
import os

from flask.ext.sqlalchemy import SQLAlchemy
from flask_heroku import Heroku

# Add your own credentials to use.
from creds import APP_KEY, APP_SECRET, ACCESS_TYPE
DROP_COOKIE = 'dropspace'

app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

class DropboxUser(db.Model):
  # The user's Dropbox uid.
  id = db.Column(db.Integer, primary_key=True)
  # A valid access token stored in format key|secret.
  token = db.Column(db.String(80))
  # The cursor from the last time the user's Dropbox data was fetched.
  cursor = db.Column(db.String(250))
  #root_id = db.Column(db.Integer)

  def __init__(self, uid, token):
    self.id = uid
    self.token = token

  def __repr__(self):
    return '<User %r>' % self.id

### MAIN Handlers ###
@app.route('/')
def index():
  sess = dropbox.session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
  uid = flask.request.cookies.get(DROP_COOKIE)
  if uid:
    try:
      dropbox_user = DropboxUser.query.filter_by(id=uid).first()
      sess.set_token(*dropbox_user.token.split('|'))
      client = dropbox.client.DropboxClient(sess)
      info = client.account_info()
      quota_info = info['quota_info']
      return flask.render_template('index.html',
                                   name=info['display_name'],
                                   used=quota_info['normal']+quota_info['shared'],
                                   quota=quota_info['quota'])
    except (AttributeError, dropbox.rest.ErrorResponse):
      # If DropboxUser not found or access token expired, try reauthenticating.
      pass

  # Authenticate user
  request_token = sess.obtain_request_token()
  flask.current_app.config[request_token.key] = request_token.to_string()
  url = sess.build_authorize_url(request_token,
                                 flask.url_for('finish_oauth', _external=True))
  return flask.render_template('login.html', dropbox_url=url)

@app.route('/finauth')
def finish_oauth():
  resp = flask.make_response(flask.redirect(flask.url_for('index')))

  # Try to obtain an access token. Set it as a cookie on the user before
  # redirecting to main page.
  uid = flask.request.args.get('uid', type=int)
  token = flask.request.args.get('oauth_token')
  stored_token = flask.current_app.config.get(token)
  if stored_token and uid:
    request_token = oauth.oauth.OAuthToken.from_string(stored_token)
    sess = dropbox.session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
    access_token = sess.obtain_access_token(request_token)
    token_str = "%s|%s" % (access_token.key, access_token.secret)
    add_dropbox_user(uid, token_str)
    resp.set_cookie(DROP_COOKIE, uid)
  else:
    app.logger.debug('No stored access token found!')
  return resp

# If user exists, update his token. Else add him.
def add_dropbox_user(uid, token):
  dropbox_user = DropboxUser(uid, token)
  db.session.merge(dropbox_user)
  db.session.commit()

### AJAX Endpoints ###
@app.route('/_spacedata')
def spacedata():
  rootdir = flask.request.args.get('root', 'dropbox', type=str)
  dropbox_uid = flask.request.args.get('uid')
  data = [['foo', 23], ['bar', 15], ['baz', 37]]
  return flask.jsonify(result=data)

# Source:
# http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
# Use this instead of filesizeformat filter b/c of open bug
# https://github.com/mitsuhiko/jinja2/pull/53.
@app.template_filter('filesizefmt')
def filesize_filter(num):
  for x in ['bytes','KB','MB','GB']:
      if num < 1024.0:
          return "%3.1f%s" % (num, x)
      num /= 1024.0
  return "%3.1f%s" % (num, 'TB')

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host = '0.0.0.0', port=port, debug=True)
