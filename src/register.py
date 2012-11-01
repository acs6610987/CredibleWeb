import webapp2
import data_models
from data_models import User
import logging
import os, jinja2
from basichandler import BasicHandler 
import hashlib

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates/')))

UNAVAILABLE_USERNAME = 1

class RegisterHandler(BasicHandler):
    def post(self):    
        username = self.request.get('username')
        user = User.gql('WHERE username = :1', username).get()
        if user:
            self.render('register.html',
                        reg_state = UNAVAILABLE_USERNAME)
            return
        userInfo = {'realname':self.request.get('realname'),
                    'username':self.request.get('username'),
                    'password':hashlib.sha1(self.request.get('password')).hexdigest(),
                    'picture':'/static/default.jpg',
                    'email':self.request.get('email'),
                    'website':self.request.get('website'),
                    'location':self.request.get('location'),
                    'expertise':self.request.get_all('expertise')}
        user = data_models.register_user(userInfo)
        data_models.store_exinfo(user.user_id, userInfo)
        
        info = {'uid':user.user_id, 'origin':'credibleweb'}
        self.set_cookies(info)
        self.redirect('/')        
    
    def get(self):
        username = self.request.get('username')
        logging.info(username)
        if username:
            user = User.gql('WHERE username = :1', username).get()
            if user:
                self.response.out.write("exist")
            else:
                self.response.out.write('available')
            return
        self.render('register.html')


app = webapp2.WSGIApplication([('/register', RegisterHandler)], 
                              debug = True)