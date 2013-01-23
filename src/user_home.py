import webapp2
from basichandler import BasicHandler
from google.appengine.ext import db
from data_models import Rating, Friends, User, PendingRequest, ExUserInfo, FacebookProfile, TwitterProfile

class UserHomeHandler(BasicHandler):
    def is_friend(self, uid):
        query1 = db.GqlQuery('SELECT user_id2 FROM Friends WHERE user_id1 = :1', self.user.user_id)
        friends = [friend.user_id2 for friend in query1]
        query2 = PendingRequest.gql('WHERE sender_id = :1', self.user.user_id)
        pending_uids = [item.receiver_id for item in query2]
        is_friend = -1
        if uid in pending_uids:
            is_friend = 0
        if uid in friends:
            is_friend = 1
        return is_friend

class UserRatingsHandler(UserHomeHandler):
    def get(self, id):
        m_user = User.gql('WHERE user_id = :1', id).get()
        query = Rating.gql('WHERE user_id = :1 ORDER BY time DESC', id)
        ratings = [rating for rating in query]
        self.render('user_ratings.html',
                    ratings = ratings,
                    user = m_user,
                    is_friend = self.is_friend(id))

class UserFollowingHandler(UserHomeHandler):
    def get(self, id):
        m_user = User.gql('WHERE user_id = :1', id).get()
        query = Friends.gql('WHERE user_id1 = :1', id)
        following_ids = [item.user_id2 for item in query]
        query = User.gql('WHERE user_id IN :1', following_ids)
        following = [item for item in query]
        self.render('user_following.html',
                    following = following,
                    user = m_user,
                    is_friend = self.is_friend(id))
           
class UserFollowersHandler(UserHomeHandler):
    def get(self, id):
        m_user = User.gql('WHERE user_id = :1', id).get()
        query = Friends.gql('WHERE user_id2 = :1', id)
        follower_ids = [item.user_id1 for item in query]
        query = User.gql('WHERE user_id IN :1', follower_ids)
        followers = [item for item in query]
        self.render('user_followers.html',
                    followers = followers,
                    user = m_user,
                    is_friend = self.is_friend(id))

class UserFriendsHandler(UserHomeHandler):
    def get(self, id):
        m_user = User.gql('WHERE user_id = :1', id).get()
        query = Friends.gql('WHERE user_id1 = :1', id)
        friend_ids = [friend.user_id2 for friend in query]
        CW_friends = []
        for uid in friend_ids:
            f = User.get_by_key_name(uid)
            CW_friends.append(f)
        self.render('user_friends.html',
                    user = m_user,
                    CW_friends = CW_friends,
                    is_friend = self.is_friend(id))
        
class UserProfileHandler(UserHomeHandler):
    def get(self, id):
        m_user =  User.gql('WHERE user_id = :1', id).get()
        cw_profile = ExUserInfo.gql('WHERE user_id = :1', m_user.user_id).get()
        fb_profile = None
        if m_user.facebook_id:
            fb_profile = FacebookProfile.gql('WHERE facebook_id = :1', m_user.facebook_id).get()
        tw_profile = None
        if m_user.twitter_id:
            tw_profile = TwitterProfile.gql('WHERE twitter_id = :1', m_user.twitter_id).get()
        self.render('user_profile.html',
                    user = m_user,
                    cw_profile = cw_profile,
                    fb_profile = fb_profile,
                    tw_profile = tw_profile,
                    is_friend = self.is_friend(id))

app = webapp2.WSGIApplication([('/user/(.*)/ratings', UserRatingsHandler),
                               ('/user/(.*)/friends', UserFriendsHandler),
                               ('/user/(.*)/following', UserFollowingHandler ),
                               ('/user/(.*)/followers', UserFollowersHandler),
                               ('/user/(.*)/profile', UserProfileHandler),
                               ('/user/(.*)', UserRatingsHandler)], 
                              debug = True)