import webapp2
from google.appengine.api import memcache
from google.appengine.ext import db
from data_models import User, Rating, Feedback, GMPoints, Friends
import Cookie
import datetime
import os, jinja2
from basichandler import BasicHandler
import import_urldata
import recommendAlg
import logging

ITEMS_EACH_BULK = 5
class HomePage(BasicHandler):
    def get(self):
#        import_urldata.test_import()
#        import_urldata.compute_diff()
        if self.user:
            recent_ratings = get_recent_ratings(self.user.user_id, 0)
#            recommendations = recommendAlg.randomAlg()
            expertise_rmds = recommendAlg.expertiseRecommend(self.user.user_id)
            sparse_rmds = recommendAlg.sparseRecommend(self.user.user_id)
            diff_rmds = recommendAlg.diffRecommend(self.user.user_id)
            self.render('homepage.html',
                        recent_ratings = recent_ratings,
                        expertise_rmds = expertise_rmds,
                        sparse_rmds = sparse_rmds,
                        diff_rmds = diff_rmds)
        else:
            self.render('welcome.html')

class NewsHandler(BasicHandler):
    def get(self):
        if self.user:
            recent_ratings = get_recent_ratings(self.user.user_id, 0)
            self.render('news.html',
                        recent_ratings = recent_ratings)
        else:
            self.render('welcome.html')

def get_recent_ratings(user_id, m_cursor):
        query1 = db.GqlQuery('SELECT user_id2 FROM Friends WHERE user_id1 = :1', user_id)
        friend_ids = [friend.user_id2 for friend in query1]
#        query2 = Rating.gql('WHERE user_id IN :1 ORDER BY time DESC LIMIT 20', friend_ids)
#        result = [item for item in query2]
        threshold_date = datetime.datetime.now() + datetime.timedelta(days=-8)
        threshold_date = threshold_date.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
        #make sure it's exactly the same query so that we can use cursor
        query2 = db.GqlQuery('SELECT * FROM Rating WHERE time > :1 ORDER BY time DESC', threshold_date)
        if m_cursor:
            query2.with_cursor(start_cursor = m_cursor)
        count = 0
        result = []
        for item in query2:
            if item.user_id in friend_ids:
                result.append(item)
                count += 1
                if count >= ITEMS_EACH_BULK:
                    break
        m_cursor = query2.cursor()
        client = memcache.Client()
        client.set(user_id+'news_cursor', m_cursor)
        return result
    

class MoreNewsHandler(BasicHandler):
    def get(self):
        client = memcache.Client()
        m_cursor = client.get(self.user.user_id + 'news_cursor')
        recent_ratings = get_recent_ratings(self.user.user_id, m_cursor)
        self.render('news_slice.html',
                    recent_ratings = recent_ratings)

class LogoutHandler(BasicHandler):
    def get(self):
        client = memcache.Client()
        client.flush_all();
        info = {'uid':None, 'origin':None, 'origin_id':None}
        self.set_cookies(info)
        self.redirect('/')
        
class PrivacyHandler(BasicHandler):
    def get(self):
        self.render('privacy.html')
        
class FeedbackHandler(BasicHandler):
    def get(self):
        self.render('feedback.html',
                    recorded = False)
        
    def post(self):
        feedback = Feedback(type = self.request.get('type'),
                            description = self.request.get('description'),
                            name = self.request.get('name'),
                            browser = self.request.get('browser'),
                            email = self.request.get('email'))
        feedback.put()
        self.render('feedback.html',
                    recorded = True)

class ExtensionHandler(BasicHandler):
    def get(self):
        self.render('extension_installation.html')
        
app = webapp2.WSGIApplication([('/', HomePage),
                               ('/news', NewsHandler),
                               ('/morenews', MoreNewsHandler),
                               ('/logoutreq', LogoutHandler),
                               ('/privacy', PrivacyHandler),
                               ('/feedback', FeedbackHandler),
                               ('/extension_installation', ExtensionHandler)], 
                              debug = True)