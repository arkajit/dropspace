import dropbox
from dropspace import client, db, session

class DropboxUser(db.Model):
  # The user's Dropbox uid.
  id = db.Column(db.Integer, primary_key=True)
  # A valid access token stored in format key|secret.
  token = db.Column(db.String(80))
  # The cursor from the last time the user's Dropbox data was fetched.
  cursor = db.Column(db.String(250))

  def __init__(self, uid, token):
    self.id = uid
    self.token = token

  def __repr__(self):
    return '<User %r>' % self.id

  # Returns access token tuple (key, secret)
  def access_token(self):
    return self.token.split('|')

  def account_info(self):
    session.set_token(*self.access_token())
    try:
      return client.account_info()
    except dropbox.rest.ErrorResponse:
      pass

  def delta(self):
    session.set_token(*self.access_token())
    cursor = self.cursor or None
    try:
      d = client.delta(cursor)
    except dropbox.rest.ErrorResponse:
      return None
    self.cursor = d['cursor']
    db.session.merge(self)
    db.session.commit()
    return d

  @classmethod
  def get_account_info(cls, id):
    user = DropboxUser.query.get(id)
    if user:
      return user.account_info()

  @classmethod
  def add_user(cls, uid, token):
    dropbox_user = DropboxUser(uid, token)
    db.session.merge(dropbox_user)
    db.session.commit()
