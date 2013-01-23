import webapp2
from basichandler import BasicHandler
from google.appengine.ext.db import stats
import random
import logging
from data_models import URLStorage
import urllib
import recommendAlg

class RandomRMDHandler(BasicHandler):
    def get(self):
#        m_stat = stats.KindStat.gql('WHERE kind_name = :1', 'URLStorage').get()
#        li = [random.randint(1, m_stat.count) for i in range(10)]
#        query = URLStorage.gql('WHERE index IN :1', li)
#        recommendations = [item for item in query]
        recommendations = recommendAlg.randomAlg()
        self.render('boredRMD.html',
                    recommendations = recommendations)

class UserRMDHandler(BasicHandler):
    def get(self):
#        m_stat = stats.KindStat.gql('WHERE kind_name = :1', 'URLStorage').get()
#        n = random.randint(1, m_stat.count)
#        recommendation = URLStorage.gql('WHERE index = :1', n).get()
        recommendation = recommendAlg.randomAlg(1)[0]
        self.redirect('/evaluate?url='+urllib.quote(recommendation.url))

class BoredRmdHandler(BasicHandler):
    def get(self):
        bored_rmds = recommendAlg.boredRecommend(self.user.user_id)
        self.render('bored_rmd.html',
                    bored_rmds = bored_rmds)
        
class HelpRmdHandler(BasicHandler):
    def get(self):
        sparse_rmds = recommendAlg.sparseRecommend(self.user.user_id)
        diff_rmds = recommendAlg.diffRecommend(self.user.user_id)
        self.render('help_rmd.html',
                    sparse_rmds = sparse_rmds,
                    diff_rmds = diff_rmds)

app = webapp2.WSGIApplication([('/randomRMD', RandomRMDHandler),
                               ('/userRMD', UserRMDHandler),
                               ('/bored_rmd', BoredRmdHandler),
                               ('/help_rmd', HelpRmdHandler)], 
                               debug = True)