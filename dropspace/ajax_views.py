from dropspace import app
from dropspace.models import DropboxUser, FileMetadata
import flask
import os.path

@app.route('/_spacedata')
def spacedata():
  uid = flask.session.get('uid', -1)
  dropbox_uid = flask.request.args.get('uid', uid, type=int)
  rootdir = flask.request.args.get('root', '/', type=str)

  data = []
  user = DropboxUser.query.get(uid)
  if user:
    fmd = user.get_absolute_path(rootdir)
    for (path, metadata) in fmd.children.items():
      relpath = os.path.relpath(path, start=rootdir)
      data.append([relpath, metadata.size])

  return flask.jsonify(result=data)

@app.route('/_quotainfo')
def quota_info():
  uid = flask.session.get('uid', -1)
  dropbox_uid = flask.request.args.get('uid', uid, type=int)
  account_info = DropboxUser.get_account_info(dropbox_uid) or {}
  quota_info = account_info.get('quota_info')
  data = []
  if quota_info:
    quota_info['free'] = quota_info['quota'] - (quota_info['normal'] +
                                                quota_info['shared'])
    del quota_info['quota']
    data = map(list, quota_info.items())
  return flask.jsonify(result=data)

