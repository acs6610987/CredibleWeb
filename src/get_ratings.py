import webapp2
from google.appengine.api import memcache
from data_models import User, Rating, URLStorage
from basichandler import BasicHandler
import recommendAlg

class GetUserRatingsHandler(BasicHandler):
    def get(self):
        if self.user:
            ratings = self.get_ratings_by_id(self.user.user_id)
#            recommendations = recommendAlg.randomAlg()
            self.render('myratings.html',
                        ratings = ratings)
        else:
            self.redirect('/')
    
    def get_ratings_by_id(self, id):
        query = Rating.gql('WHERE user_id = :1 ORDER BY time DESC', id)
        result = [item for item in query]
        return result

class GetUrlRatingsHandler(BasicHandler):
    def get(self):
        url = self.request.get('url')
        query = Rating.gql('WHERE url = :1 ORDER BY time DESC', url)
        ratings = [item for item in query]
        self.render('url_ratings.html',
                    ratings = ratings)

class GetStatusRatingsHandler(BasicHandler):
    def get(self):
        url = self.request.get('url')
        status = []
        avg = 0
        total = 0
        m_stat = URLStorage.gql('WHERE url = :1', url).get()
        if m_stat:
            status = m_stat.ratings
            total = m_stat.total
            avg = 0
            if total != 0:
                avg = sum([(i+1)*status[i] for i in range(5)])*1.0 / total
            status.reverse()
            
        (truthfulness, unbiased, security, design) = self.get_details(url)
        
        self.render('status_table.html',
                    status = status,
                    url = url,
                    avg = avg,
                    truthfulness = truthfulness,
                    unbiased = unbiased,
                    security = security,
                    design = design,
                    total = total)
        
    def get_details(self, url):
        query = Rating.gql('WHERE url = :1', url)
        ratings = [item for item in query]
        list1 = [item.truthfulness for item in ratings if item.truthfulness > 0]
        list2 = [item.unbiased for item in ratings if item.unbiased > 0]
        list3 = [item.security for item in ratings if item.security > 0]
        list4 = [item.design for item in ratings if item.design > 0]
        truthfulness = 0
        unbiased = 0
        security = 0
        design = 0
        if list1:
            truthfulness = float(sum(list1)) / len(list1)
        if list2:
            unbiased = float(sum(list2)) / len(list2)
        if list3:
            security = float(sum(list3)) / len(list3)
        if list4:
            design = float(sum(list4)) / len(list4)
        return (truthfulness, unbiased, security, design)

app = webapp2.WSGIApplication([('/getratings_user', GetUserRatingsHandler),
                               ('/getratings_url', GetUrlRatingsHandler),
                               ('/getratings_status', GetStatusRatingsHandler)], 
                              debug = True)