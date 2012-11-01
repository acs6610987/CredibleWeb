import webapp2
from google.appengine.api import memcache, urlfetch
from data_models import User, Rating
import Cookie
import datetime
import os, jinja2
from basichandler import BasicHandler
import urllib
import conf
import logging


class EvaluateHandler(BasicHandler):
    def get(self):
        if self.user:
            url = self.request.get('url')
            logging.info(url)
            permit = self.check_X_Frame_Options(url)
#            status_table = urlfetch.fetch(conf.WEB_SERVER+'/geteval_status?url='+url).content
            self.render('evaluate.html',
                        url = url,
                        permit = permit)
        else:
            self.render('welcome.html')
    
    def post(self): 
        if self.user:
            rating = int(self.request.get('rating'))
            url = self.request.get('url')
            logging.info(url)
            self.store_rating_data(self.user.user_id, url, rating)
            self.response.out.write("We have successfully processed your rating! Please return and close this page!")
        else:
            self.render('welcome.html')
            
    def store_rating_data(self, user_id, url, rating):
        query = Rating.gql('WHERE user_id = :1 AND url = :2', user_id, url)
        rating_entry = query.get()
        if rating_entry:
            rating_entry.rating = rating
            rating_entry.put()
        else:
            rating_entry = Rating(user_id = user_id,
                                  url = url,
                                  rating = rating)
            rating_entry.put()
    
    def check_X_Frame_Options(self, url):
        try:
#            pageInfo = urllib.urlopen(url).info()
            pageInfo = urlfetch.fetch(url).headers
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