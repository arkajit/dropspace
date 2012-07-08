import dropbox
import flask
import oauth
import os

app = flask.Flask(__name__)

APP_KEY = '7tklqprz9csy80z'
APP_SECRET = '0g2kziivrbwj74y'
ACCESS_TYPE = 'dropbox'
DROP_COOKIE = 'dropspace'

@app.route('/')
def index():
  sess = dropbox.session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
  access_token = flask.request.cookies.get(DROP_COOKIE)
  if access_token:
    sess.set_token(*access_token.split('|'))
    client = dropbox.client.DropboxClient(sess)
    info = client.account_info()
    return flask.render_template('index.html',
                                 name=info['display_name'],
                                 quota=info['quota_info']['quota'])
  else:
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

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host = '0.0.0.0', port=port, debug=True)
