from dropspace import app, session
from dropspace.models import DropboxUser
import flask
import oauth

@app.route('/stats')
def stats():
  uid = flask.session.get('uid', -1)
  user = DropboxUser.query.get(uid)
  account_info = {}
  if user:
    account_info = user.account_info()

  if account_info:
    flask.session['loggedin'] = True
    quota_info = account_info['quota_info']
    return flask.render_template('stats.html',
                                 name=account_info['display_name'],
                                 used=quota_info['normal']+quota_info['shared'],
                                 quota=quota_info['quota'])
  else:
    flask.session.pop('uid', None)
    return flask.redirect(flask.url_for('login'))

@app.route('/')
@app.route('/login')
def login():
  flask.session['loggedin'] = False
  if 'uid' in flask.session:
    return flask.render_template('login.html',
        dropbox_url=flask.url_for('stats'))
  else:
    request_token = session.obtain_request_token()
    flask.session[request_token.key] = request_token.to_string()
    login_url = session.build_authorize_url(
                    request_token,
                    flask.url_for('finish_oauth', _external=True))
    return flask.render_template('login.html', dropbox_url=login_url)

@app.route('/finauth')
def finish_oauth():
  uid = flask.request.args.get('uid', type=int)
  token = flask.request.args.get('oauth_token')
  stored_token = flask.session.get(token)
  if stored_token and uid:
    request_token = oauth.oauth.OAuthToken.from_string(stored_token)
    access_token = session.obtain_access_token(request_token)
    token_str = "%s|%s" % (access_token.key, access_token.secret)
    DropboxUser.add_user(uid, token_str)
    flask.session['uid'] = uid
  else:
    app.logger.debug('No stored access token found!')

  return flask.redirect(flask.url_for('stats'))
