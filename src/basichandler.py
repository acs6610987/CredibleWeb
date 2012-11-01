#!/usr/bin/env python
# coding: utf-8

import webapp2
from google.appengine.api import urlfetch, memcache
import os, jinja2
from data_models import User, Friends, Rating
import Cookie
import datetime
import logging
import conf
import call_api
import urllib
import twitter_oauth
import math

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates/')))

def datetimeformat(value):
    return value.strftime('%a, %d %b %Y %H:%M:%S')
def is_friend(id1, id2):
    result = Friends.gql('WHERE user_id1 = :1 AND user_id2 = :2', id1, id2).get()
    if result:
        return True
    return False

def heaven_bottom(uid):
    num = Rating.gql('WHERE user_id = :1', uid).count()
    e_mx = math.exp(-num/30.0)
    fp = (1-e_mx) / (1+e_mx)
    return int(fp*150+10)

def heaven_left(uid):
    num = Rating.gql('WHERE user_id = :1', uid).count()
    e_mx = math.exp(-num/30.0)
    fp = (1-e_mx) / (1+e_mx)
    return int(fp*150+10)

def num_of_ratings(uid):
    num = Rating.gql('WHERE user_id = :1', uid).count()
    return num

def has_expertise(list, expertise):
    if expertise in list:
        return 'checked="checked"'
    return ''

def get_name_by_id(id):
    tmpUser = User.get_by_key_name(id)
    return tmpUser.realname

def datetime_format(t):
    return t.strftime('%a, %d %b %Y %H:%M:%S')

def encode_url(url):
    logging.info(urllib.quote(url))
    return urllib.quote(url)

jinja_environment.filters['datetimeformat'] = datetimeformat
jinja_environment.filters['is_friend'] = is_friend
jinja_environment.filters['heaven_bottom'] = heaven_bottom
jinja_environment.filters['heaven_left'] = heaven_left
jinja_environment.filters['num_of_ratings'] = num_of_ratings
jinja_environment.filters['has_expertise'] = has_expertise
jinja_environment.filters['get_name_by_id'] = get_name_by_id
jinja_environment.filters['datetime_format'] = datetime_format
jinja_environment.filters['encode_url'] = encode_url

class BasicHandler(webapp2.RequestHandler):
    user = None
    origin = None
    origin_user = None
    def initialize(self, request, response):
        super(BasicHandler, self).initialize(request, response)
        self.retrieve_user_info(request)
        logging.info(self.request)
        
    def retrieve_user_info(self, request):
        info = {}
        info['uid'] = request.cookies.get('uid')
        if not info['uid']:
            return
        info['origin'] = request.cookies.get('origin')
        info['origin_id'] = request.cookies.get('origin_id')
        
        self.user = User.get_by_key_name(info['uid'])
        self.origin = info['origin']
#        if self.origin == 'facebook':
#            self.origin_user = FacebookUser.get_by_key_name(info['origin_id'])
#        elif self.origin == 'twitter':
#            self.origin_user = TwitterUser.get_by_key_name(info['origin_id'])
    
    def set_cookies(self, info):
        for name, value in info.items():
            cookie = Cookie.SimpleCookie()
            expires = datetime.timedelta(days = 1)
            if not value:
                value = 'deleted'
                expires = datetime.timedelta(minutes = -1000)
            cookie[name] = value
            cookie[name]['path'] = '/'
            expires = datetime.datetime.now() + expires
            expires = expires.strftime('%a, %d %b %Y %H:%M:%S')
            cookie[name]['expires'] = expires
            self.response.headers.add_header(*cookie.output().split(': ', 1))
    
    def render(self, file, **data):
        if not data:
            data = {}
        data['logged_in_user'] = self.user
        data['origin'] = self.origin
        template = jinja_environment.get_template(file)
        self.response.out.write(template.render(data))
    
    def facebook_auth(self, callback):
        code = self.request.get('code')
#        logging.info(code)
        if not code:
            self.redirect('https://www.facebook.com/dialog/oauth?'+
                'client_id=' + conf.FACEBOOK_APP_ID +
                '&redirect_uri=' + conf.WEB_SERVER + callback +
                '&scope=user_location,user_website' +
                '&state=zhicong')
        state = self.request.get('state')
#        logging.info(state)
        if state == 'zhicong':
            tokenUrl = ('https://graph.facebook.com/oauth/access_token?' +
                'client_id=' + conf.FACEBOOK_APP_ID +
                '&redirect_uri=' + conf.WEB_SERVER + callback +
                '&client_secret=' + conf.FACEBOOK_APP_SECRET + 
                '&code=' + code)

            response = urlfetch.fetch(tokenUrl).content
#            logging.info(response)
            tokenInfo = self.get_key_value_from_string(response)
            access_token = tokenInfo['access_token']
            expires = datetime.datetime.now() + datetime.timedelta(seconds=int(tokenInfo['expires']))
                
            params = {'fields':'id,name,username,picture,location,website', 'access_token':access_token}
            userInfo = call_api.facebook_api('GET', '/me', params)
            m_userInfo = {'facebook_id':userInfo['id'],
                          'realname':userInfo.get('name') or '',
                          'username':userInfo.get('username') or '',
                          'picture':userInfo['picture']['data']['url'],
                          'fb_access_token':access_token,
                          'location':userInfo['location']['name'] if userInfo.has_key('location') else '',
                          'website':userInfo.get('website') or ''}
            return m_userInfo
        return None
    
    def twitter_auth(self, callback):
        oauth_token = self.request.get('oauth_token')
        oauth_verifier = self.request.get('oauth_verifier')
        if not oauth_token:
            oauth_header = twitter_oauth.get_oauth_header(
                                                        'POST', conf.TWITTER_API+'/oauth/request_token',
                                                        None, conf.WEB_SERVER+callback,
                                                        conf.TWITTER_CONSUMER_KEY, 
                                                        conf.TWITTER_CONSUMER_SECRET)
            step1 = urlfetch.fetch(conf.TWITTER_API+'/oauth/request_token', 
                                   method = urlfetch.POST, 
                                   headers={u'Authorization':oauth_header}).content
            step1_response = self.get_key_value_from_string(step1)
            self.redirect(conf.TWITTER_API+'/oauth/authenticate?oauth_token='+step1_response['oauth_token'])
        else:
            params = {'oauth_verifier':oauth_verifier}
            oauth_header = twitter_oauth.get_oauth_header('POST', 
                                                          conf.TWITTER_API+'/oauth/access_token', 
                                                          params, None, 
                                                          conf.TWITTER_CONSUMER_KEY, 
                                                          conf.TWITTER_CONSUMER_SECRET, 
                                                          oauth_token, None)
            logging.info(oauth_header)
            payload = 'oauth_verifier='+oauth_verifier
            step3 = urlfetch.fetch(conf.TWITTER_API+'/oauth/access_token',
                                   payload = payload,
                                   method = urlfetch.POST,
                                   headers={u'Authorization':oauth_header,
                                            u'Content-Type':'application/x-www-form-urlencoded'}).content
            logging.info(step3)
            step3_response = self.get_key_value_from_string(step3)
            twitter_id = step3_response['user_id']
            oauth_token = step3_response['oauth_token']
            oauth_token_secret = step3_response['oauth_token_secret']
            
            params = {'user_id':twitter_id}
            userInfo = call_api.twitter_api('GET', '/1.1/users/show.json', 
                                            params, oauth_token, 
                                            oauth_token_secret)
            m_userInfo = {'twitter_id':twitter_id,
                          'realname':userInfo.get('name') or '',
                          'username':userInfo.get('screen_name') or '',
                          'picture':userInfo['profile_image_url'],
                          'tw_access_token':oauth_token,
                          'tw_token_secret':oauth_token_secret,
                          'location':userInfo.get('location') or '',
                          'website':userInfo.get('url') or ''}
            return m_userInfo
        return None
            
    def get_key_value_from_string(self,str):
        info = str.split('&')
        params = {}
        for param in info:
            k, v = map(urllib.unquote, param.split('='))
            params[k] = v
        return params