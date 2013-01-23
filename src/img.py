import webapp2
from google.appengine.ext import db
import logging


class ImageHandler (webapp2.RequestHandler):
    def get(self):
        extra = db.get(self.request.get("img_id"))
        if extra.photo:
            self.response.headers['Content-Type'] = "image/jpeg"
            self.response.out.write(extra.photo)
        else:
            self.error(404)
          
class BlobSnapshotHandler(webapp2.RedirectHandler):
    def get(self):
        ss = db.get(self.request.get('key'))
        if ss.snapshot:
            self.response.headers['Content-Type'] = "image/jpeg"
            self.response.out.write(ss.snapshot)
        else:
            self.error(404)
            
app = webapp2.WSGIApplication([('/img', ImageHandler),
                               ('/img/blob_snapshot', BlobSnapshotHandler)],
                              debug = True)