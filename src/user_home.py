import webapp2
from basichandler import BasicHandler
from data_models import Rating, Friends, User

class UserRatingsHandler(BasicHandler):
    def get(self, id):
        m_user = User.gql('WHERE user_id = :1', id).get()
        query = Rating.gql('WHERE user_id = :1', id)
        ratings = [rating for rating in query]
        self.render('user_ratings.html',
                    ratings = ratings,
                    user = m_user)

class UserFollowingHandler(BasicHandler):
    def get(self, id):
        m_user = User.gql('WHERE user_id = :1', id).get()
        query = Friends.gql('WHERE user_id1 = :1', id)
        following_ids = [item.user_id2 for item in query]
        query = User.gql('WHERE user_id IN :1', following_ids)
        following = [item for item in query]
        self.render('user_following.html',
                    following = following,
                    user = m_user)
        
class UserFollowersHandler(BasicHandler):
    def get(self, id):
        m_user = User.gql('WHERE user_id = :1', id).get()
        query = Friends.gql('WHERE user_id2 = :1', id)
        follower_ids = [item.user_id1 for item in query]
        query = User.gql('WHERE user_id IN :1', follower_ids)
        followers = [item for item in query]
        self.render('user_followers.html',
                    followers = followers,
                    user = m_user)

app = webapp2.WSGIApplication([('/user/(.*)/ratings', UserRatingsHandler),
                               ('/user/(.*)/following', UserFollowingHandler ),
                               ('/user/(.*)/followers', UserFollowersHandler),
                               ('/user/(.*)', UserRatingsHandler)], 
                              debug = True)