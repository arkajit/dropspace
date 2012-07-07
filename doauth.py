from dropbox import client, rest, session

APP_KEY = '7tklqprz9csy80z'
APP_SECRET = '0g2kziivrbwj74y'
ACCESS_TYPE = 'dropbox'

sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
request_token = sess.obtain_request_token()
url = sess.build_authorize_url(request_token)

# Make the user sign in and authorize this token
print "url:", url
print "Please visit this website and press the 'Allow' button, then hit 'Enter' here."
raw_input()

# This will fail if the user didn't visit the above URL and hit 'Allow'
access_token = sess.obtain_access_token(request_token)

client = client.DropboxClient(sess)
info = client.account_info()
username = info['display_name'].lower().replace(' ', '')
print info
f = open("%s.tok" % username, 'w')
f.write(access_token.to_string())
