import webapp2
from google.appengine.api import memcache
from data_models import User, Rating
import Cookie
import datetime
import os, jinja2
import logging
from basichandler import BasicHandler
import recommendAlg

class GetEvalHandler(BasicHandler):
    def get(self):
        if self.user:
            recommendations = recommendAlg.randomAlg()
            self.render('geturl.html',
                        recommendations = recommendations)
        else:
            self.redirect('/')

class GetStatusHandler(BasicHandler):
    def get(self):
        url = self.request.get('url')
        logging.info(url)
        ratings = Rating.gql('WHERE url = :1 ORDER BY rating DESC', url)
        status = []
        last = -1
        index = -1
        sum = 0
        num = 0
        avg = 0
        for item in ratings:
            if item.rating == last:
                status[index] = (last, status[index][1] + 1)
            else:
                status.append((item.rating, 1))
                last = item.rating
                index += 1
            sum += item.rating
            num += 1
        if num != 0:
            avg = float(sum) / num
        self.render('status_table.html',
                    status = status,
                    url = url,
                    avg = avg)
        
                

app = webapp2.WSGIApplication([('/geteval', GetEvalHandler),
                               ('/geteval_status', GetStatusHandler)], 
                              debug = True)