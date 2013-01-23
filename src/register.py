import webapp2
import data_models
from data_models import User
import logging
import os, jinja2
from basichandler import BasicHandler 
import hashlib

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates/')))

UNAVAILABLE_EMAIL = 1

class RegisterHandler(BasicHandler):
    def post(self):    
        email = self.request.get('email')
        user = User.gql('WHERE email = :1', email).get()
        if user:
            self.render('register.html',
                        reg_state = UNAVAILABLE_EMAIL,
                        email = email)
            return
        firstname = self.request.get('firstname').capitalize()
        lastname = self.request.get('lastname').capitalize()
        userInfo = {'firstname':firstname,
                    'lastname':lastname,
                    'realname':firstname+' '+lastname,
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
        email = self.request.get('email')
        if email:
            user = User.gql('WHERE email = :1', email).get()
            if user:
                self.response.out.write("exist")
            else:
                self.response.out.write('available')
            return
        self.render('register.html',
                    reg_state = 0,
                    email = '')


app = webapp2.WSGIApplication([('/register', RegisterHandler)], 
                              debug = True)