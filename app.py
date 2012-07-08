import dropbox
import flask
import oauth
import os

# Add your own credentials to use.
from creds import APP_KEY, APP_SECRET, ACCESS_TYPE

app = flask.Flask(__name__)

DROP_COOKIE = 'dropspace'

### MAIN Handlers ###
@app.route('/')
def index():
  sess = dropbox.session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
  access_token = flask.request.cookies.get(DROP_COOKIE)
  if access_token:
    sess.set_token(*access_token.split('|'))
    client = dropbox.client.DropboxClient(sess)
    try:
      info = client.account_info()
      return flask.render_template('index.html',
                                   name=info['display_name'],
                                   quota=info['quota_info']['quota'])
    except dropbox.rest.ErrorResponse:
      pass

  # No access token (or expire/revoked). Reauthenticate.
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
  uid = flask.request.args.get('uid')
  token = flask.request.args.get('oauth_token')
  stored_token = flask.current_app.config.get(token)
  if stored_token:
    request_token = oauth.oauth.OAuthToken.from_string(stored_token)
    sess = dropbox.session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
    access_token = sess.obtain_access_token(request_token)
    resp.set_cookie(DROP_COOKIE,
                    "%s|%s" % (access_token.key, access_token.secret))
  else:
    app.logger.debug('No stored access token found!')
  return resp

### AJAX Endpoints ###
@app.route('/_spacedata')
def spacedata():
  rootdir = flask.request.args.get('root', 'dropbox', type=str)
  data = [['foo', 23], ['bar', 15], ['baz', 37]]
  return flask.jsonify(result=data)

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host = '0.0.0.0', port=port, debug=True)
