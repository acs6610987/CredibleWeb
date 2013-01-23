import webapp2
from google.appengine.api import memcache
from google.appengine.ext import db
from data_models import User, PendingRequest
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
            self.render('search_hint.html',
                        hint = hint,
                        keyword = urllib.quote(keyword))
        else:
            results = self.search_user(keyword)
            self.render('search_result.html',
                        results = results)
        
    def search_user_hint(self, keyword):
        keyword = keyword.lower()
        query = User.all()
        results = query.fetch(limit=100)
        hint = []
        number = 0;
        for tmpuser in results:
            if tmpuser.user_id == self.user.user_id:
                continue
            if tmpuser.realname.lower().find(keyword) >= 0:
                name = tmpuser.realname
            else:
                continue
            hint.append(tmpuser)
            number += 1
            if number >= 4:
                break
        return hint
    def search_user(self, keyword):
        keyword = keyword.lower()
        query1 = db.GqlQuery('SELECT user_id2 FROM Friends WHERE user_id1 = :1', self.user.user_id)
        friends = [friend.user_id2 for friend in query1]
        query2 = PendingRequest.gql('WHERE sender_id = :1', self.user.user_id)
        pending_uids = [item.receiver_id for item in query2]
        query3 = User.all()
        results = []
        for tmpuser in query3:
            if tmpuser.user_id == self.user.user_id:
                continue
            if tmpuser.realname.lower().find(keyword) < 0:
                continue
            is_friend = -1
            if tmpuser.user_id in pending_uids:
                is_friend = 0
            if tmpuser.user_id in friends:
                is_friend = 1
            results.append({'user':tmpuser, 
                            'is_friend':is_friend})
        return results
        
app = webapp2.WSGIApplication([('/search', SearchHandler)], 
                              debug = True)