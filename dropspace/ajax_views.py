from dropspace import app
from dropspace.filters import filesize_filter
from dropspace.models import DropboxUser, FileMetadata
import flask
import os.path

@app.route('/_delta')
def process_delta():
  uid = flask.session.get('uid', -1)
  dropbox_uid = flask.request.args.get('uid', uid, type=int)
  user = DropboxUser.query.get(dropbox_uid)
  output = {'success': False, 'num_deltas': 0}
  if user:
    output['num_deltas'] = user.delta()
    output['success'] = True
  return flask.jsonify(result=output)

@app.route('/_spacedata')
def spacedata():
  uid = flask.session.get('uid', -1)
  dropbox_uid = flask.request.args.get('uid', uid, type=int)
  rootdir = flask.request.args.get('root', '/', type=str)
  if rootdir != '/':
    rootdir = rootdir.rstrip('/')

  data = []
  files = []
  filestable = ''
  totsum = 0
  user = DropboxUser.query.get(dropbox_uid)
  if user:
    fmd = user.get_absolute_path(rootdir)
    if fmd and fmd.path == rootdir:
      for (path, metadata) in fmd.children.items():
        relpath = os.path.relpath(path, start=rootdir)
        # TODO(arkajit): What about empty directories?
        if len(metadata.children) > 0:
          data.append([relpath, metadata.size])
        else:
          files.append({'name': relpath, 'size': metadata.size})
      filesum = sum(f['size'] for f in files)
      data.append(['Files', filesum])
      totsum = filesize_filter(sum(d[1] for d in data))
      files.sort(key=lambda f: f['size'], reverse=True)
      files.append({'name': 'Total', 'size': filesum})
      filestable = flask.render_template('table.html', files=files)

  return flask.jsonify(result=data, filestable=filestable, total=totsum)

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

