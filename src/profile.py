import webapp2
from basichandler import BasicHandler
from data_models import ExUserInfo, FacebookProfile, TwitterProfile
import logging
from google.appengine.api import images
from google.appengine.ext import db
import conf
    

class ProfileHandler(BasicHandler):
    def get(self):
        cw_profile = ExUserInfo.gql('WHERE user_id = :1', self.user.user_id).get()
        fb_profile = None
        if self.user.facebook_id:
            fb_profile = FacebookProfile.gql('WHERE facebook_id = :1', self.user.facebook_id).get()
        tw_profile = None
        if self.user.twitter_id:
            tw_profile = TwitterProfile.gql('WHERE twitter_id = :1', self.user.twitter_id).get()
        self.render('profile.html',
                    cw_profile = cw_profile,
                    fb_profile = fb_profile,
                    tw_profile = tw_profile,
                    success = False)
    
    def post(self):
        cw_profile = ExUserInfo.gql('WHERE user_id = :1', self.user.user_id).get()
        self.user.realname = self.request.get('realname')
        
        
        cw_profile.email = self.request.get('email')
        cw_profile.website = self.request.get('website')
        cw_profile.location = self.request.get('location')
        cw_profile.expertise = self.request.get_all('expertise')
        
        photo = self.request.get('photo')
        if photo:
            if conf.WEB_SERVER == 'http://credibleweb.appspot.com':
                photo = images.resize(photo, 100, 100)
            cw_profile.photo = db.Blob(photo)
            self.user.picture = '/img?img_id=%s' % cw_profile.key()
        
        self.user.put()
        cw_profile.put()
        
#       retrieve social network profiles
        fb_profile = None
        if self.user.facebook_id:
            fb_profile = FacebookProfile.gql('WHERE facebook_id = :1', self.user.facebook_id).get()
        tw_profile = None
        if self.user.twitter_id:
            tw_profile = TwitterProfile.gql('WHERE twitter_id = :1', self.user.twitter_id).get()
        self.render('profile.html',
                    cw_profile = cw_profile,
                    fb_profile = fb_profile,
                    tw_profile = tw_profile,
                    success = True)

app = webapp2.WSGIApplication([('/editprofile', ProfileHandler)], 
                              debug = True)