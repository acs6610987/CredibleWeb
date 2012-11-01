import webapp2
from data_models import User
from basichandler import BasicHandler
import call_api
from google.appengine.api import memcache
from google.appengine.ext import db
import logging

FRIENDS_EACH_BULK = 24

class GetFriendHandler(BasicHandler):
    def get(self):
        FB_friends = None
        TW_friends = None
        CW_following = None
        CW_followers = None
        if self.user.facebook_id:
            FB_friends = self.getFBFriend(True)
        if self.user.twitter_id:
            TW_friends = self.getTWFriend(True)
        CW_following = self.getCWFollowing()
        CW_followers = self.getCWFollowers()
        self.render('friends.html',
                    FB_friends = FB_friends,
                    TW_friends = TW_friends,
                    CW_following = CW_following,
                    CW_followers = CW_followers)
        
        
    def getFBFriend(self, reload):
        client = memcache.Client()
        friend_ids = client.get(self.user.user_id+'fb_fids')
        cursor = client.get(self.user.user_id+'fb_cursor')
        if not friend_ids or reload:
            params = {'fields':'friends', 'access_token': self.user.fb_access_token}
            response = call_api.facebook_api('GET', '/me', params)
            friend_ids = [friend['id'] for friend in response['friends']['data']]
            cursor = 0
            client.add(self.user.user_id+'fb_fids', friend_ids)
            client.add(self.user.user_id+'fb_cursor', cursor)
        
        logging.info(cursor)
        if cursor >= len(friend_ids):
            return {}
            
        if cursor + FRIENDS_EACH_BULK > len(friend_ids):
            next_part = friend_ids[cursor:]
        else:
            next_part = friend_ids[cursor:(cursor + FRIENDS_EACH_BULK)]
        cursor += FRIENDS_EACH_BULK
        
        logging.info(next_part)
        params = {'ids':','.join([str(id) for id in next_part]), 
                  'fields':'id,name,picture'}
        response = call_api.facebook_api('GET', '/', params)
        FB_friends = []
        for id, friendInfo in response.items():
            FB_friends.append({'id':friendInfo['id'], 
                               'name':friendInfo['name'], 
                               'picture':friendInfo['picture']['data']['url']})
        client.set(self.user.user_id+'fb_cursor', cursor)
        return FB_friends
            
        
    def getTWFriend(self, reload):
        client = memcache.Client()
        friend_ids = client.get(self.user.user_id+'tw_fids')
        cursor = client.get(self.user.user_id+'tw_cursor')
        if not friend_ids or reload:
            params = {'user_id':self.user.twitter_id,
                      'cursor':'-1'}
            response = call_api.twitter_api('GET', '/1.1/friends/ids.json', params, 
                                 self.user.tw_access_token, 
                                 self.user.tw_token_secret)
            friend_ids = response['ids']
            cursor = 0
            client.add(self.user.user_id+'tw_fids', friend_ids)
            client.add(self.user.user_id+'tw_cursor', cursor)
        
        logging.info(cursor)
        if cursor >= len(friend_ids):
            return {}
        if cursor + FRIENDS_EACH_BULK > len(friend_ids):
            next_part = friend_ids[cursor:]
        else:
            next_part = friend_ids[cursor:(cursor + FRIENDS_EACH_BULK)]
        cursor += FRIENDS_EACH_BULK
        
        logging.info(next_part)
        params = {'user_id':','.join([str(id) for id in next_part])}
        response = call_api.twitter_api('GET', '/1.1/users/lookup.json', params, 
                                        self.user.tw_access_token, 
                                        self.user.tw_token_secret)
        TW_friends = []
        for friend in response:
            TW_friends.append({'id':friend['id_str'],
                               'name':friend['name'],
                               'picture':friend['profile_image_url']})
        client.set(self.user.user_id+'tw_cursor', cursor)
        return TW_friends
        
    def getCWFollowing(self):
        query1 = db.GqlQuery('SELECT user_id2 FROM Friends WHERE user_id1 = :1', self.user.user_id)
        friend_ids = [friend.user_id2 for friend in query1]
        query2 = db.GqlQuery('SELECT * FROM User WHERE user_id IN :1', friend_ids)
        CW_following = [tmpuser for tmpuser in query2]
        return CW_following
    
    def getCWFollowers(self):
        query1 = db.GqlQuery('SELECT user_id1 FROM Friends WHERE user_id2 = :1', self.user.user_id)
        friend_ids = [friend.user_id1 for friend in query1]
        query2 = db.GqlQuery('SELECT * FROM User WHERE user_id IN :1', friend_ids)
        CW_followers = [tmpuser for tmpuser in query2]
        return CW_followers

class FacebookGetFriendHandler(GetFriendHandler):
    def get(self):
        nextslice = self.request.get('nextslice')
        if not nextslice:
            FB_friends = self.getFBFriend(True)
            self.render('FB_friends.html',
                        FB_friends = FB_friends)
        else:
            FB_friends = self.getFBFriend(False)
            if FB_friends:
                self.render('friends_slice.html',
                            friends = FB_friends)
            else:
                self.response.out.write('done')
        
class TwitterGetFriendHandler(GetFriendHandler):
    def get(self):
        nextslice = self.request.get('nextslice')
        if not nextslice:
            TW_friends = self.getTWFriend(True)
            self.render('TW_friends.html',
                        TW_friends = TW_friends)
        else:
            TW_friends = self.getTWFriend(False)
            if TW_friends:
                self.render('friends_slice.html',
                            friends = TW_friends)
            else:
                self.response.out.write('done')
         
class CrediblewebGetFriendHandler(GetFriendHandler):
    def get(self):
        if self.user:
            friends = self.get_friends()
            self.render('crediblewebfriends.html',
                        friends = friends)    
        else:
            self.redirect('/')
    
    def get_friends(self):
        query1 = db.GqlQuery('SELECT user_id2 FROM Friends WHERE user_id1 = :1', self.user.user_id)
        friend_ids = [friend.user_id2 for friend in query1]
        query2 = db.GqlQuery('SELECT * FROM User WHERE user_id IN :1', friend_ids)
        friends = [tmpuser for tmpuser in query2]
        return friends
            
    
app = webapp2.WSGIApplication([('/friends', GetFriendHandler),
                               ('/facebookfriends', FacebookGetFriendHandler),
                               ('/twitterfriends', TwitterGetFriendHandler),
                               ('/crediblewebfriends', CrediblewebGetFriendHandler)], 
                              debug = True)