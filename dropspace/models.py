import dropbox
from dropspace import client, db, session
import os.path
from sqlalchemy.orm.collections import attribute_mapped_collection

class DropboxUser(db.Model):
  # The user's Dropbox uid.
  id = db.Column(db.Integer, primary_key=True)
  # A valid access token stored in format key|secret.
  token = db.Column(db.String(80))
  # The cursor from the last time the user's Dropbox data was fetched.
  cursor = db.Column(db.String(250))

  # Id of the root of the user's Dropbox.
  root_id = db.Column(db.Integer, db.ForeignKey('file_metadata.id'))
  root = db.relationship(
      'FileMetadata',
      backref=db.backref('owner', uselist=False, cascade='all, delete-orphan'),
      cascade='all, delete-orphan',
      single_parent=True)

  def __init__(self, uid, token):
    self.id = uid
    self.token = token
    self.cursor = None

  def __repr__(self):
    return '<User(id=%r, root=%r)>' % (self.id, self.root)

  # Returns access token tuple (key, secret)
  def access_token(self):
    return self.token.split('|')

  def account_info(self):
    session.set_token(*self.access_token())
    try:
      return client.account_info()
    except dropbox.rest.ErrorResponse:
      pass

  # Return the user's file at the given absolute path, if one exists.
  # Else return the deepest directory that could contain the file.
  def get_absolute_path(self, abspath):
    if not self.root:
      return None
    return self.root.get_relative_path(os.path.relpath(abspath, '/'))

  def delta(self):
    session.set_token(*self.access_token())
    cursor = self.cursor or None
    try:
      d = client.delta(cursor)
      print "Got delta with %d entries." % len(d['entries'])
    except dropbox.rest.ErrorResponse:
      return None

    if d['reset']:
      self.root = FileMetadata(path='/', size=0)
    for (path, metadata) in d['entries']:
      print "Procesing path: %s" % path
      old_file = self.get_absolute_path(path)
      if old_file and old_file.path == path:
        if not metadata:
          old_file.parent = None
        else:
          old_file.size = metadata['bytes']
      elif metadata:
        relpath = os.path.relpath(path, old_file.path)
        new_file = old_file.add_all_children(relpath)
        new_file.size = metadata['bytes']
    self.cursor = d['cursor']
    print "About to merge user..."
    db.session.merge(self)
    print "About to commit..."
    db.session.commit()

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

class FileMetadata(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  path = db.Column(db.String(500), nullable=False)
  size = db.Column(db.BigInteger)
  parent_id = db.Column(db.Integer, db.ForeignKey('file_metadata.id'),
                        index=True)
  children = db.relationship(
      'FileMetadata',
      cascade='all, delete-orphan',
      backref=db.backref('parent', remote_side=id),
      collection_class=attribute_mapped_collection('path'),
      innerjoin=True,
      join_depth=2,
      lazy="joined",
      single_parent=True)

  def __init__(self, path, size, parent=None, owner=None):
    self.path = path
    self.size = size
    self.parent = parent
    self.owner = owner

  # Adds a child if it is does not already exist.
  def add_child(self, name):
    abspath = os.path.join(self.path, name)
    if name != '' and abspath not in self.children:
      child = FileMetadata(abspath, size=0)
      self.children[abspath] = child
      return child

  # Adds all missing children on the provided relative path.
  # Returns the node at the newly created path.
  def add_all_children(self, relpath):
    toks = relpath.split('/', 1)
    child = self.add_child(toks[0])
    if child and len(toks) == 2:
      return child.add_all_children(toks[1])
    else:
      return child

  # Returns a child node with the given name if one exists.
  def get_child(self, name):
    return self.children.get(os.path.normpath(os.path.join(self.path, name)))

  # Given a path relative to the current node, return it if it exists.
  # Otherwise return the deepest node on the path that does exist.
  def get_relative_path(self, relpath):
    toks = relpath.split('/', 1)
    child = self.get_child(toks[0])
    if child:
      if len(toks) == 2:
        return child.get_relative_path(toks[1])
      else:
        return child
    else:
      return self

  def get_size(self):
    if len(self.children) == 0:
      return self.size
    else:
      return sum([c.get_size() for c in self.children.values()])

  def __repr__(self):
    return '<FileMetadata(id=%r, path=%r, size=%r)>' % (self.id, self.path, self.size)
