import webapp2
from google.appengine.api import memcache
from data_models import User, Rating, URLStorage
import Cookie
import datetime
import os, jinja2
import logging
from basichandler import BasicHandler
import recommendAlg

class GetEvalHandler(BasicHandler):
    def get(self):
        if self.user:
#            recommendations = recommendAlg.randomAlg()
            expertise_rmds = recommendAlg.expertiseRecommend(self.user.user_id)
            sparse_rmds = recommendAlg.sparseRecommend(self.user.user_id)
            diff_rmds = recommendAlg.diffRecommend(self.user.user_id)
            self.render('geturl.html',
                        expertise_rmds = expertise_rmds,
                        sparse_rmds = sparse_rmds,
                        diff_rmds = diff_rmds)
        else:
            self.redirect('/')
            
app = webapp2.WSGIApplication([('/geteval', GetEvalHandler)], 
                              debug = True)