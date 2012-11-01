import webapp2
from google.appengine.api import memcache
from data_models import User
from data_models import Rating
from basichandler import BasicHandler
import recommendAlg

class GetRatingsHandler(BasicHandler):
    def get(self):
        if self.user:
            ratings = self.get_ratings_by_id(self.user.user_id)
            recommendations = recommendAlg.randomAlg()
            self.render('myratings.html',
                        ratings = ratings,
                        recommendations = recommendations)
        else:
            self.redirect('/')
    
    def get_ratings_by_id(self, id):
        tmpuser = User.get_by_key_name(id)
        name = tmpuser.realname or tmpuser.username;
        query = Rating.gql('WHERE user_id = :1 ORDER BY time DESC', id)
        result = [item for item in query]
        return result
#        for item in query:
#            result += """
#                <li>
#                    %s rate <span class="evalscore">%d</span> on webpage <span class="evalurl" onclick="open_page('%s')">%s</span>.  ---%s
#                </li>
#                <hr />
#            """ % (name, item.rating, item.url, item.url, item.time.strftime('%a, %d %b %Y %H:%M:%S'))
#        return result

app = webapp2.WSGIApplication([('/getratings', GetRatingsHandler)], 
                              debug = True)