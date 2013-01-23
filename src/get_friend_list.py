import webapp2
from data_models import User, FBFriends, TWFriends, Friends
from basichandler import BasicHandler
import call_api
from google.appengine.api import memcache
from google.appengine.ext import db
import logging

FRIENDS_EACH_BULK = 24

class GetFriendHandler(BasicHandler):
    def get(self):
        FB_friends = None
        current_fb_on_cw = 0
        total_fb_on_cw = 0
        TW_friends = None
        current_tw_on_cw = 0
        total_tw_on_cw = 0
        CW_friends = None
#        CW_following = None
#        CW_followers = None
        if self.user.facebook_id:
            (FB_friends, current_fb_on_cw, total_fb_on_cw) = self.getFBFriend(True)
        if self.user.twitter_id:
            (TW_friends, current_tw_on_cw, total_tw_on_cw) = self.getTWFriend(True)
#        CW_following = self.getCWFollowing()
#        CW_followers = self.getCWFollowers()
        CW_friends = self.getCWFriends()
        self.render('friends.html',
                    FB_friends = FB_friends,
                    current_fb_on_cw = current_fb_on_cw,
                    total_fb_on_cw = total_fb_on_cw,
                    TW_friends = TW_friends,
                    current_tw_on_cw = current_tw_on_cw,
                    total_tw_on_cw = total_tw_on_cw,
                    CW_friends = CW_friends)
#                    CW_following = CW_following,
#                    CW_followers = CW_followers)
        
        
    def getFBFriend(self, reload):
        client = memcache.Client()
#        friend_ids = client.get(self.user.user_id+'fb_fids')
        m_friends = FBFriends.gql('WHERE facebook_id = :1', self.user.facebook_id).get()
        friend_ids = m_friends.friends
        cursor = client.get(self.user.user_id+'fb_cursor')
        logging.info('reload:  '+str(reload))
        logging.info('cursor:  '+str(cursor))
#        if not friend_ids or reload:
        if reload:
#            params = {'fields':'friends', 'access_token': self.user.fb_access_token}
#            response = call_api.facebook_api('GET', '/me', params)
#            friend_ids = [friend['id'] for friend in response['friends']['data']]
            cursor = 0
#            client.add(self.user.user_id+'fb_fids', friend_ids)
#            client.add(self.user.user_id+'fb_cursor', cursor)
        
        if cursor >= len(friend_ids):
            return ({}, 0, m_friends.num_on_cw)
            
        if cursor + FRIENDS_EACH_BULK > len(friend_ids):
            next_part = friend_ids[cursor:]
        else:
            next_part = friend_ids[cursor:(cursor + FRIENDS_EACH_BULK)]
        cursor += FRIENDS_EACH_BULK
        
        params = {'ids':','.join([str(id) for id in next_part]), 
                  'fields':'id,name,picture'}
        response = call_api.facebook_api('GET', '/', params)
        FB_friends = []
        current_cws = 0
        for id, friendInfo in response.items():
            fb_friend = {'id':friendInfo['id'], 
                         'name':friendInfo['name'], 
                         'picture':friendInfo['picture']['data']['url']}
            if id in friend_ids[:m_friends.num_on_cw]:
                tmpuser = User.gql('WHERE facebook_id = :1', id).get()
                fb_friend['uid'] = tmpuser.user_id
                FB_friends.insert(0, fb_friend)
                current_cws += 1
            else:
                FB_friends.append(fb_friend)
        client.set(self.user.user_id+'fb_cursor', cursor)
        return (FB_friends, current_cws, m_friends.num_on_cw)
            
        
    def getTWFriend(self, reload):
        client = memcache.Client()
#        friend_ids = client.get(self.user.user_id+'tw_fids')
        m_friends = TWFriends.gql('WHERE twitter_id = :1', self.user.twitter_id).get()
        friend_ids = m_friends.friends
        cursor = client.get(self.user.user_id+'tw_cursor')
#        if not friend_ids or reload:
        if reload:
#            params = {'user_id':self.user.twitter_id,
#                      'cursor':'-1'}
#            response = call_api.twitter_api('GET', '/1.1/friends/ids.json', params, 
#                                 self.user.tw_access_token, 
#                                 self.user.tw_token_secret)
#            friend_ids = response['ids']
            cursor = 0
#            client.add(self.user.user_id+'tw_fids', friend_ids)
#            client.add(self.user.user_id+'tw_cursor', cursor)
        
        if cursor >= len(friend_ids):
            return ({}, 0, m_friends.num_on_cw)
        if cursor + FRIENDS_EACH_BULK > len(friend_ids):
            next_part = friend_ids[cursor:]
        else:
            next_part = friend_ids[cursor:(cursor + FRIENDS_EACH_BULK)]
        cursor += FRIENDS_EACH_BULK
        
        params = {'user_id':','.join([str(id) for id in next_part])}
        response = call_api.twitter_api('GET', '/1.1/users/lookup.json', params, 
                                        self.user.tw_access_token, 
                                        self.user.tw_token_secret)
        TW_friends = []
        current_cws = 0
        for friend in response:
            tw_friend = {'id':friend['id_str'],
                         'name':friend['name'],
                         'picture':friend['profile_image_url']}
            if friend['id_str'] in friend_ids[:m_friends.num_on_cw]:
                tmpuser = User.gql('WHERE twitter_id = :1', friend['id_str']).get()
                tw_friend['uid'] = tmpuser.user_id
                TW_friends.insert(0, tw_friend)
                current_cws += 1
            else:
                TW_friends.append(tw_friend)
        client.set(self.user.user_id+'tw_cursor', cursor)
        return (TW_friends, current_cws,  m_friends.num_on_cw)
        
    def getCWFriends(self):
        query = Friends.gql('WHERE user_id1 = :1', self.user.user_id)
        friend_ids = [friend.user_id2 for friend in query]
        CW_friends = []
        for uid in friend_ids:
            f = User.get_by_key_name(uid)
            CW_friends.append(f)
        return CW_friends
        
    def getCWFollowing(self):
        query1 = db.GqlQuery('SELECT user_id2 FROM Friends WHERE user_id1 = :1', self.user.user_id)
        friend_ids = [friend.user_id2 for friend in query1]
        query2 = db.GqlQuery('SELECT * FROM User WHERE user_id IN :1', friend_ids) #don't user IN, since it has a limit 30
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
            (FB_friends, current_fb_on_cw, total_fb_on_cw) = self.getFBFriend(True)
            self.render('FB_friends.html',
                        FB_friends = FB_friends,
                        current_fb_on_cw = current_fb_on_cw,
                        total_fb_on_cw = total_fb_on_cw)
        else:
            (FB_friends, current_fb_on_cw, total_fb_on_cw) = self.getFBFriend(False)
            if FB_friends:
                self.render('friends_slice.html',
                            friends = FB_friends,
                            current_on_cw = current_fb_on_cw)
            else:
                self.response.out.write('done')
        
class TwitterGetFriendHandler(GetFriendHandler):
    def get(self):
        nextslice = self.request.get('nextslice')
        if not nextslice:
            (TW_friends, current_tw_on_cw, total_tw_on_cw) = self.getTWFriend(True)
            self.render('TW_friends.html',
                        TW_friends = TW_friends,
                        current_tw_on_cw = current_tw_on_cw,
                        total_tw_on_cw = total_tw_on_cw)
        else:
            (TW_friends, current_tw_on_cw, total_tw_on_cw) = self.getTWFriend(False)
            if TW_friends:
                self.render('friends_slice.html',
                            friends = TW_friends,
                            current_on_cw = current_tw_on_cw)
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