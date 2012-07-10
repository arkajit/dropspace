# Custom Jinja2 Filters: These are usable in the templates.

from dropspace import app

# Source:
# http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
# Use this instead of filesizeformat filter b/c of open bug
# https://github.com/mitsuhiko/jinja2/pull/53.
@app.template_filter('filesizefmt')
def filesize_filter(num):
  for x in ['bytes','KB','MB','GB']:
      if num < 1024.0:
          return "%3.1f%s" % (num, x)
      num /= 1024.0
  return "%3.1f%s" % (num, 'TB')
