import webapp2
from google.appengine.api import memcache
from google.appengine.ext import db
from data_models import User
from data_models import Rating
from basichandler import BasicHandler
import conf
import urllib

class SearchHandler(BasicHandler):
    def get(self):
        keyword = self.request.get('keyword')
        ishint = self.request.get('hint')
        if ishint:
            hint = self.search_user_hint(keyword)
            self.response.out.write(hint)
        else:
            results = self.search_user(keyword)
            self.render('search_result.html',
                        results = results)
        
    def search_user_hint(self, keyword):
        keyword = keyword.lower()
        query = db.GqlQuery('SELECT realname, username FROM User')
        results = query.fetch(limit=100)
        hint = ""
        number = 0;
        for tmpuser in results:
            if tmpuser.realname.lower().find(keyword) >= 0:
                name = tmpuser.realname
            else:
                continue
            hint += """
                <li>
                    <a href="%s/search?keyword=%s">%s</a>
                </li>
            """ % (conf.WEB_SERVER, urllib.quote(name), name)
            number += 1
            if number >= 4:
                break
        return hint
    def search_user(self, keyword):
        keyword = keyword.lower()
        query1 = db.GqlQuery('SELECT user_id2 FROM Friends WHERE user_id1 = :1', self.user.user_id)
        friends = [friend.user_id2 for friend in query1]
        query2 = db.GqlQuery('SELECT user_id, realname, username, picture FROM User')
        results = []
        for tmpuser in query2:
            if tmpuser.realname.lower().find(keyword) < 0:
                continue
            
            results.append({'user':tmpuser, 
                            'is_friend':tmpuser.user_id in friends})
        return results
        
app = webapp2.WSGIApplication([('/search', SearchHandler)], 
                              debug = True)