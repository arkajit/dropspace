from dropspace import app
from dropspace.models import DropboxUser
import flask

@app.route('/_spacedata')
def spacedata():
  rootdir = flask.request.args.get('root', 'dropbox', type=str)
  dropbox_uid = flask.request.args.get('uid')
  data = [['foo', 23], ['bar', 15], ['baz', 37]]
  return flask.jsonify(result=data)

@app.route('/_quotainfo')
def quota_info():
  dropbox_uid = flask.request.args.get('uid', type=int)
  account_info = DropboxUser.get_account_info(dropbox_uid) or {}
  quota_info = account_info.get('quota_info')
  data = []
  if quota_info:
    quota_info['free'] = quota_info['quota'] - (quota_info['normal'] +
                                                quota_info['shared'])
    del quota_info['quota']
    data = map(list, quota_info.items())
  return flask.jsonify(result=data)


