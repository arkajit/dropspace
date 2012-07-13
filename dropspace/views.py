from dropspace import app, session, COOKIE_NAME
from dropspace.models import DropboxUser
import flask
import oauth

@app.route('/')
def index():
  uid = flask.request.cookies.get(COOKIE_NAME)
  account_info = DropboxUser.get_account_info(uid)
  if account_info:
    quota_info = account_info['quota_info']
    return flask.render_template('index.html',
                                 name=account_info['display_name'],
                                 used=quota_info['normal']+quota_info['shared'],
                                 quota=quota_info['quota'])
  else:
    return flask.redirect(flask.url_for('login'))

@app.route('/login')
def login():
  login_url = flask.url_for('index')
  # Build authorization URL if we don't already know the user id.
  if not flask.request.cookies.get(COOKIE_NAME):
      request_token = session.obtain_request_token()
      flask.current_app.config[request_token.key] = request_token.to_string()
      login_url = session.build_authorize_url(
                      request_token,
                      flask.url_for('finish_oauth', _external=True))

  return flask.render_template('login.html', dropbox_url=login_url)

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
    access_token = session.obtain_access_token(request_token)
    token_str = "%s|%s" % (access_token.key, access_token.secret)
    DropboxUser.add_user(uid, token_str)
    resp.set_cookie(COOKIE_NAME, uid)
  else:
    app.logger.debug('No stored access token found!')
  return resp
