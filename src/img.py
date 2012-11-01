import webapp2
from google.appengine.ext import db


class ImageHandler (webapp2.RequestHandler):
    def get(self):
        extra = db.get(self.request.get("img_id"))
        if extra.photo:
            self.response.headers['Content-Type'] = "image/jpeg"
            self.response.out.write(extra.photo)
        else:
            self.error(404)
          
app = webapp2.WSGIApplication([('/img', ImageHandler)], 
                              debug = True)