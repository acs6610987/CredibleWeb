#Description: TODO
#Created by: Zhicong Huang
#Authors: Zhicong Huang, Alexandra Olteanu
#Copyright: EPFL 2013

import webapp2
from google.appengine.api import urlfetch, memcache
from google.appengine.ext import db
import os, jinja2
import data_models
from data_models import User, Friends, Rating, GMPoints, PendingRequest, URLStorage
import Cookie
import datetime
import logging
import conf
import call_api
import urllib
import twitter_oauth
import math
import gmp_rules
import gae_cache
import json 

TOP_NUM = 3
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates/')))

def datetimeformat(value):
    return value.strftime('%a, %d %b %Y %H:%M:%S')

def is_friend(id1, id2):
    result = Friends.gql('WHERE user_id1 = :1 AND user_id2 = :2', id1, id2).get()
    if result:
        return True
    return False

def mywot_score(url):
    url.strip()
    tokens = url.split('//')
    if len(tokens)>1:
        tokens = tokens[1].split('/')
    else:
        tokens = url.split('/')  
    reputation = json.loads(urllib.urlopen("http://api.mywot.com/0.4/public_link_json2?hosts=%s/&key=%s" % (tokens[0], conf.MYWOT_KEY) ).read())
    if '0' in reputation[tokens[0]]:
        return reputation[tokens[0]]['0'][0]
    else:
        return 0

def heaven_bottom(uid):
    gmp = gmp_rules.get_user_gmp(uid)
    level = int(math.log(gmp.total_points, data_models.LogScale))
    base = math.pow(data_models.LogScale, level)
    top = math.pow(data_models.LogScale, level+1)
    k = data_models.LevelHeight / (top - base)
    return k*(gmp.total_points - base) + data_models.LevelHeight*level

def heaven_left(uid):
    gmp = gmp_rules.get_user_gmp(uid)
    level = int(math.log(gmp.total_points, data_models.LogScale))
    base = math.pow(data_models.LogScale, level)
    top = math.pow(data_models.LogScale, level+1)
    k = data_models.LevelHeight / (top - base)
    return k*(gmp.total_points - base) + data_models.LevelHeight*level

def num_of_ratings(uid):
    num = Rating.gql('WHERE user_id = :1', uid).count()
    return num

def has_expertise(list, expertise):
    if expertise in list:
        return 'checked="checked"'
    return ''

def get_expertise_text(expertise):
    return ', '.join([data_models.EXPERTISES[item] for item in expertise])

def get_name_by_id(id):
    tmpUser = User.gql('WHERE user_id = :1', id).get()
    return tmpUser.realname

def datetime_format(t):
    return t.strftime('%a, %d %b %Y %H:%M:%S')

def encode_url(url):
    return urllib.quote(url)

def get_points(uid):
    gmp = gmp_rules.get_user_gmp(uid)
    return gmp.total_points

def get_status(uid):
    gmp = gmp_rules.get_user_gmp(uid)
    if(gmp.total_points >= data_models.OverallStatus['Master']):
        return 'Master'
    if(gmp.total_points >= data_models.OverallStatus['Expert']):
        return 'Expert'
    if(gmp.total_points >= data_models.OverallStatus['Enthusiast']):
        return 'Enthusiast'
    if(gmp.total_points >= data_models.OverallStatus['Beginner']):
        return 'Beginner'
    return 'Novice'

def get_level(uid):
    gmp = gmp_rules.get_user_gmp(uid)
    level = int(math.log(int(gmp.total_points), data_models.LogScale))
    return level

def get_picture_by_id(uid):
    user = User.gql('WHERE user_id = :1', uid).get()
    return user.picture

def get_uid_by_fbid(fbid):
    user = User.gql('WHERE facebook_id = :1', fbid).get()
    return user.user_id

def get_topic_text(topic):
    return data_models.EXPERTISES[topic]

def get_reward_points(url, user):
    return gmp_rules.worth_points(url, user)

def get_friendreq_num(uid):
    reqs = PendingRequest.gql('WHERE receiver_id = :1', uid)
    return reqs.count()

def get_avg(ratings):
    total = sum(ratings)
    avg = 0
    if total:
        avg = sum([(i+1)*ratings[i] for i in range(5)])*1.0 / total
    return avg

def get_url_info(url):
    info = URLStorage.gql('WHERE url = :1', url).get()
    return info
        
def get_top_users(self_id):
    query = db.GqlQuery('SELECT * FROM GMPoints ORDER BY total_points DESC LIMIT 3')
    tops = []
    for top in query:
        if top.user_id != self_id:
            tops.append(top.user_id)
    return tops
    
def get_top_friends(self_id):
    query1 = GMPoints.all()
    query2 = Friends.gql('WHERE user_id1 = :1', self_id)
    friend_ids = [f.user_id2 for f in query2]
    top_friends = []
    num = 0
    for top in query1:
        if top.user_id in friend_ids:
            top_friends.append(top.user_id)
            num += 1
            if num >= TOP_NUM:
                break
    return top_friends

jinja_environment.filters['datetimeformat'] = datetimeformat
jinja_environment.filters['is_friend'] = is_friend
jinja_environment.filters['heaven_bottom'] = heaven_bottom
jinja_environment.filters['heaven_left'] = heaven_left
jinja_environment.filters['num_of_ratings'] = num_of_ratings
jinja_environment.filters['has_expertise'] = has_expertise
jinja_environment.filters['get_expertise_text'] = get_expertise_text
jinja_environment.filters['get_name_by_id'] = get_name_by_id
jinja_environment.filters['datetime_format'] = datetime_format
jinja_environment.filters['encode_url'] = encode_url
jinja_environment.filters['get_points'] = get_points
jinja_environment.filters['get_status'] = get_status
jinja_environment.filters['get_level'] = get_level
jinja_environment.filters['get_picture_by_id'] = get_picture_by_id
jinja_environment.filters['get_uid_by_fbid'] = get_uid_by_fbid
jinja_environment.filters['get_topic_text'] = get_topic_text
jinja_environment.filters['get_reward_points'] = get_reward_points
jinja_environment.filters['get_friendreq_num'] = get_friendreq_num
jinja_environment.filters['get_avg'] = get_avg
jinja_environment.filters['get_url_info'] = get_url_info
jinja_environment.filters['get_top_users'] = get_top_users
jinja_environment.filters['get_top_friends'] = get_top_friends
jinja_environment.filters['mywot_score'] = mywot_score

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
        if not code:
            self.redirect('https://www.facebook.com/dialog/oauth?'+
                'client_id=' + conf.FACEBOOK_APP_ID +
                '&redirect_uri=' + conf.WEB_SERVER + callback +
                '&scope=user_location,user_website' +
                '&state=zhicong')
        state = self.request.get('state')
        if state == 'zhicong':
            tokenUrl = ('https://graph.facebook.com/oauth/access_token?' +
                'client_id=' + conf.FACEBOOK_APP_ID +
                '&redirect_uri=' + conf.WEB_SERVER + callback +
                '&client_secret=' + conf.FACEBOOK_APP_SECRET + 
                '&code=' + code)

            response = urlfetch.fetch(tokenUrl).content
            tokenInfo = self.get_key_value_from_string(response)
            access_token = tokenInfo['access_token']
            expires = datetime.datetime.now() + datetime.timedelta(seconds=int(tokenInfo['expires']))
                
            params = {'fields':'id, first_name, last_name, name,username,picture,location,website,friends', 'access_token':access_token}
            userInfo = call_api.facebook_api('GET', '/me', params)
            m_userInfo = {'facebook_id':userInfo['id'],
                          'firstname': userInfo.get('first_name').capitalize(),
                          'lastname': userInfo.get('last_name').capitalize(),
                          'realname':userInfo.get('name') or '',
                          'username':userInfo.get('username') or '',
                          'picture':userInfo['picture']['data']['url'],
                          'fb_access_token':access_token,
                          'location':userInfo['location']['name'] if userInfo.has_key('location') else '',
                          'website':userInfo.get('website') or '',
                          'friends':[friend['id'] for friend in userInfo['friends']['data']] if userInfo.has_key('friends') else []}
            return m_userInfo
        return None
    
    # authentication with twitter (the steps closely follow those explained at https://dev.twitter.com/docs/auth/implementing-sign-twitter)
    def twitter_auth(self, callback):
        oauth_token = self.request.get('oauth_token')
        oauth_verifier = self.request.get('oauth_verifier')
        
        # check if the users has already granted access 
        if not oauth_token:
            # step 1 - obtaining a request token
            
            # generate the oauth header
            oauth_header = twitter_oauth.get_oauth_header(
                                                        'POST', conf.TWITTER_API+'/oauth/request_token',
                                                        None, conf.WEB_SERVER+callback,
                                                        conf.TWITTER_CONSUMER_KEY, 
                                                        conf.TWITTER_CONSUMER_SECRET)
            
            #sending a signed message to POST oauth/request_token
            step1 = urlfetch.fetch(conf.TWITTER_API+'/oauth/request_token', 
                                   method = urlfetch.POST, 
                                   headers={u'Authorization':oauth_header}).content
                                   
            step1_response = self.get_key_value_from_string(step1)
            
            #step 2 - redirecting the user
            self.redirect(conf.TWITTER_API+'/oauth/authenticate?oauth_token='+step1_response['oauth_token'])
            
        else: # if access has been granted
            params = {'oauth_verifier':oauth_verifier}
            oauth_header = twitter_oauth.get_oauth_header('POST', 
                                                          conf.TWITTER_API+'/oauth/access_token', 
                                                          params, None, 
                                                          conf.TWITTER_CONSUMER_KEY, 
                                                          conf.TWITTER_CONSUMER_SECRET, 
                                                          oauth_token, None)
            payload = 'oauth_verifier='+oauth_verifier
            step3 = urlfetch.fetch(conf.TWITTER_API+'/oauth/access_token',
                                   payload = payload,
                                   method = urlfetch.POST,
                                   headers={u'Authorization':oauth_header,
                                            u'Content-Type':'application/x-www-form-urlencoded'}).content
            step3_response = self.get_key_value_from_string(step3)
            twitter_id = step3_response['user_id']
            oauth_token = step3_response['oauth_token']
            oauth_token_secret = step3_response['oauth_token_secret']
            
            #get basic user information
            params = {'user_id':twitter_id}
            userInfo = call_api.twitter_api('GET', '/1.1/users/show.json', 
                                            params, oauth_token, 
                                            oauth_token_secret)
            #get friends
            params = {'user_id':twitter_id,
                      'cursor':'-1'}
            response = call_api.twitter_api('GET', '/1.1/friends/ids.json', params, 
                                 oauth_token, 
                                 oauth_token_secret)
            friends = [str(id) for id in response['ids']]
            
            m_userInfo = {'twitter_id':twitter_id,
                          'firstname':(userInfo.get('name') or '').capitalize(),
                          'lastname':'',
                          'realname':userInfo.get('name') or '',
                          'username':userInfo.get('screen_name') or '',
                          'picture':userInfo['profile_image_url'],
                          'tw_access_token':oauth_token,
                          'tw_token_secret':oauth_token_secret,
                          'location':userInfo.get('location') or '',
                          'website':userInfo.get('url') or '',
                          'friends':friends}
            return m_userInfo
        return None
    
    def linkedin_auth(self, callback):
        linkedin_code = self.request.get('linkedin_code')
            
    def get_key_value_from_string(self,str):
        info = str.split('&')
        params = {}
        for param in info:
            k, v = map(urllib.unquote, param.split('='))
            params[k] = v
        return params