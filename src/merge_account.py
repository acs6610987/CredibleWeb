import webapp2
from basichandler import BasicHandler
import conf
from google.appengine.api import urlfetch
import tools
import datetime
import call_api
import data_models
import twitter_oauth

class MergeHandler(BasicHandler):
    def get(self):
        if self.user:
            self.render('merge.html',
                        info = '')
        else:
            self.redirect('/')
 
class FacebookMergeHandler(BasicHandler):
    def get(self):
        userInfo = self.facebook_auth('/facebookmerge')
        if userInfo:
            info = data_models.merge_facebook(self.user, userInfo)
            self.render('merge.html',
                        info = info)
    
class TwitterMergeHandler(BasicHandler):
    def get(self):
        userInfo = self.twitter_auth('/twittermerge')
        if userInfo:
            info = data_models.merge_twitter(self.user, userInfo)
            self.render('merge.html',
                        info = info)

app = webapp2.WSGIApplication([('/accountmerge', MergeHandler),
                               ('/facebookmerge', FacebookMergeHandler),
                               ('/twittermerge', TwitterMergeHandler)], 
                              debug = True)