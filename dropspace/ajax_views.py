from dropspace import app
from dropspace.models import DropboxUser
import flask
import json

@app.route('/_spacedata')
def spacedata():
  uid = flask.session.get('uid', -1)
  dropbox_uid = flask.request.args.get('uid', uid, type=int)
  try:
    f = open("deltas/%s" % dropbox_uid)
    paths = json.load(f)
  except Exception:
    return flask.jsonify(result=[])

  data = []
  rootdir = flask.request.args.get('root', '/foo', type=str)
  if rootdir in paths:
    for child in paths[rootdir]['names']:
      child_size = paths["%s/%s" % (rootdir, child)]['bytes']
      data.append([child, child_size])
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

