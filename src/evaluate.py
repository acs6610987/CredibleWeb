import webapp2
from google.appengine.api import memcache, urlfetch
import data_models
from data_models import User, Rating, GMPoints, URLStorage, Statistics
import Cookie
import datetime
import os, jinja2
from basichandler import BasicHandler
import urllib
import conf
import logging
import gmp_rules
import recommendAlg

class EvaluateHandler(BasicHandler):
    def get(self):
        if self.user:
            url = self.request.get('url')
            permit = self.check_X_Frame_Options(url)
            points = gmp_rules.worth_points(url, self.user)
            url_info = URLStorage.gql('WHERE url = :1', url).get()
            expertise_rmds = recommendAlg.expertiseRecommend(self.user.user_id)
            sparse_rmds = recommendAlg.sparseRecommend(self.user.user_id)
            diff_rmds = recommendAlg.diffRecommend(self.user.user_id)
            self.render('evaluate.html',
                        url = url,
                        permit = permit,
                        points = points,
                        url_info = url_info,
                        expertise_rmds = expertise_rmds,
                        sparse_rmds = sparse_rmds,
                        diff_rmds = diff_rmds)
        else:
            self.render('welcome.html')
    
    def post(self): 
        if self.user:
            url = self.request.get('url')
            points = gmp_rules.worth_points(url, self.user)
            rating = self.store_rating_data()
            self.gain_points(points)
            gmp_rules.worth_points(url, self.user, True)   #update cache
            self.render('submitted_review.html',
                        item = rating)
        else:
            self.render('welcome.html')
            
    def store_rating_data(self):
        overall_rating = int(self.request.get('overall_rating'))
        url = self.request.get('url')
        comment = self.request.get('comment')
        truthfulness = int(self.request.get('truthfulness'))
        unbiased = int(self.request.get('unbiased'))
        security = int(self.request.get('security'))
        design = int(self.request.get('design'))
        
        query = Rating.gql('WHERE user_id = :1 AND url = :2', self.user.user_id, url)
        rating_entry = query.get()
        oldrating = 0
        if rating_entry:
            oldrating = rating_entry.rating
            rating_entry.rating = overall_rating
            rating_entry.comment = comment
            rating_entry.truthfulness = truthfulness
            rating_entry.unbiased = unbiased
            rating_entry.security = security
            rating_entry.design = design
            rating_entry.attempts += 1
            rating_entry.put()
        else:
            rating_id = data_models.generate_rid()
            rating_entry = Rating(key_name = rating_id,
                                  rating_id = rating_id,
                                  user_id = self.user.user_id,
                                  url = url,
                                  rating = overall_rating,
                                  comment = comment,
                                  truthfulness = truthfulness,
                                  unbiased = unbiased,
                                  security = security,
                                  design = design,
                                  attempts = 1,
                                  upvotes = 0)
            rating_entry.put()
        data_models.update_url_storage(url, oldrating, overall_rating)
#        data_models.test_update_url_storage(url, oldrating, overall_rating)
        return rating_entry
    
    def gain_points(self, points):
        gmp_rules.rule_rating_award(points, self.user)
        
    def check_X_Frame_Options(self, url):
        try:
#            pageInfo = urllib.urlopen(url).info()
            pageInfo = urlfetch.fetch(url, deadline=60).headers
        except:
            return -1
        if not pageInfo.has_key('X-Frame-Options'):
            return 1
        option = pageInfo['X-Frame-Options'].upper()
        if  option == 'SAMEORIGIN' or option == 'DENY':
            return 0
        return 1

app = webapp2.WSGIApplication([('/evaluate', EvaluateHandler)], 
                              debug = True)