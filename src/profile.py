import webapp2
from basichandler import BasicHandler
import data_models
from data_models import ExUserInfo, FacebookProfile, TwitterProfile
import logging
from google.appengine.api import images
from google.appengine.ext import db
import conf
import call_api
    

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

class EditProfileHandler(BasicHandler):
    def get(self):
        cw_profile = ExUserInfo.gql('WHERE user_id = :1', self.user.user_id).get()
        self.render('edit_cwprofile.html',
                    cw_profile = cw_profile)
        
    def post(self):
        cw_profile = ExUserInfo.gql('WHERE user_id = :1', self.user.user_id).get()
        self.user.firstname = self.request.get('firstname').capitalize()
        self.user.lastname = self.request.get('lastname').capitalize()
        self.user.realname = self.user.firstname + ' ' + self.user.lastname
#
#        
#        cw_profile.email = self.request.get('email')
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

class UpdateFBProfileHandler(BasicHandler):
    def get(self):
        params = {'fields':'id,name,username,picture,location,website,friends', 'access_token':self.user.fb_access_token}
        userInfo = call_api.facebook_api('GET', '/me', params)
        m_userInfo = {'facebook_id':userInfo['id'],
                      'realname':userInfo.get('name') or '',
                      'username':userInfo.get('username') or '',
                      'picture':userInfo['picture']['data']['url'],
                      'location':userInfo['location']['name'] if userInfo.has_key('location') else '',
                      'website':userInfo.get('website') or '',
                      'friends':[friend['id'] for friend in userInfo['friends']['data']] if userInfo.has_key('friends') else []}
        data_models.update_facebook_info(self.user, m_userInfo)
        data_models.update_facebook_friends(self.user, m_userInfo)
        self.redirect('/profile')
        
class UpdateTWProfileHandler(BasicHandler):
    def get(self):
        #get basic user information
        params = {'user_id':self.user.twitter_id}
        userInfo = call_api.twitter_api('GET', '/1.1/users/show.json', 
                                        params, self.user.tw_access_token, 
                                        self.user.tw_token_secret)
        #get friends
        params = {'user_id':self.user.twitter_id,
                  'cursor':'-1'}
        response = call_api.twitter_api('GET', '/1.1/friends/ids.json', params, 
                                        self.user.tw_access_token, 
                                        self.user.tw_token_secret)
        friends = [str(id) for id in response['ids']]
        
        m_userInfo = {'twitter_id':self.user.twitter_id,
                      'realname':userInfo.get('name') or '',
                      'username':userInfo.get('screen_name') or '',
                      'picture':userInfo['profile_image_url'],
                      'location':userInfo.get('location') or '',
                      'website':userInfo.get('url') or '',
                      'friends':friends}
        data_models.update_twitter_info(self.user, m_userInfo)
        data_models.update_twitter_friends(self.user, m_userInfo)
        self.redirect('/profile')
 
class FacebookMergeHandler(BasicHandler):
    def get(self):
        userInfo = self.facebook_auth('/facebookmerge')
        if userInfo:
            info = data_models.merge_facebook(self.user, userInfo)
            self.redirect('/profile')
    
class TwitterMergeHandler(BasicHandler):
    def get(self):
        userInfo = self.twitter_auth('/twittermerge')
        if userInfo:
            info = data_models.merge_twitter(self.user, userInfo)
            self.redirect('/profile')

app = webapp2.WSGIApplication([('/profile', ProfileHandler),
                               ('/edit_cwprofile', EditProfileHandler),
                               ('/update_fbprofile', UpdateFBProfileHandler),
                               ('/update_twprofile', UpdateTWProfileHandler),
                               ('/facebookmerge', FacebookMergeHandler),
                               ('/twittermerge', TwitterMergeHandler)], 
                              debug = True)