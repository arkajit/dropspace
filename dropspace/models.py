import dropbox
from dropspace import client, db, session

class DropboxUser(db.Model):
  # A unique, increasing key (NOT the dropbox id).
  id = db.Column(db.Integer, primary_key=True)
  # The user's Dropbox uid.
  uid = db.Column(db.Integer, unique=True)
  # A valid access token stored in format key|secret.
  token = db.Column(db.String(80))
  # The cursor from the last time the user's Dropbox data was fetched.
  cursor = db.Column(db.String(250))
  #root_id = db.Column(db.Integer)

  def __init__(self, uid, token):
    self.uid = uid
    self.token = token

  def __repr__(self):
    return '<User %r>' % self.id

  # Returns access token tuple (key, secret)
  def access_token(self):
    return self.token.split('|')

  @classmethod
  def get_account_info(cls, uid):
    user = DropboxUser.query.filter_by(uid=uid).first()
    if user:
      session.set_token(*user.access_token())
      try:
        return client.account_info()
      except dropbox.rest.ErrorResponse:
        pass

  @classmethod
  def add_user(cls, uid, token):
    dropbox_user = DropboxUser(uid, token)
    db.session.merge(dropbox_user)
    db.session.commit()
