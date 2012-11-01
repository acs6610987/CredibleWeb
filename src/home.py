import webapp2
from google.appengine.api import memcache
from google.appengine.ext import db
from data_models import User, Rating, Feedback
import Cookie
import datetime
import os, jinja2
from basichandler import BasicHandler
import import_urldata
import recommendAlg

class HomePage(BasicHandler):
    def get(self):
#        import_urldata.test_import()
        if self.user:
            recent_ratings = get_recent_ratings(self.user.user_id)
            recommendations = recommendAlg.randomAlg()
            self.render('homepage.html',
                        recent_ratings = recent_ratings,
                        recommendations = recommendations)
        else:
            self.render('welcome.html')
#        for item in query2:
#            tmpUser = User.get_by_key_name(item.user_id)
#            result += """
#                <li>
#                    %s rate <span class="evalscore">%d</span> on webpage <span class="evalurl" onclick="open_page('%s')">%s</span>.  ---%s
#                </li>
#                <hr />
#            """ % (tmpUser.realname, item.rating, item.url, item.url, item.time.strftime('%a, %d %b %Y %H:%M:%S'))
#        return result

class NewsHandler(BasicHandler):
    def get(self):
        if self.user:
            recent_ratings = get_recent_ratings(self.user.user_id)
            recommendations = recommendAlg.randomAlg()
            self.render('news.html',
                        recent_ratings = recent_ratings,
                        recommendations = recommendations)
        else:
            self.render('welcome.html')

def get_recent_ratings(user_id):
        query1 = db.GqlQuery('SELECT user_id2 FROM Friends WHERE user_id1 = :1', user_id)
        friend_ids = [friend.user_id2 for friend in query1]
        query2 = Rating.gql('WHERE user_id IN :1 ORDER BY time DESC LIMIT 20', friend_ids)
        result = [item for item in query2]
        return result
    
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
                               ('/logoutreq', LogoutHandler),
                               ('/privacy', PrivacyHandler),
                               ('/feedback', FeedbackHandler),
                               ('/extension_installation', ExtensionHandler)], 
                              debug = True)