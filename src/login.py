#!/usr/bin/env python
# coding: utf-8

import webapp2
from google.appengine.api import urlfetch, memcache
import twitter_oauth
import conf
import urllib
import json
import call_api
import data_models
from data_models import User 
import logging
import datetime
import os, jinja2
from basichandler import BasicHandler
import hashlib

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates/')))

class TwitterLogin(BasicHandler):
    def get(self):
        userInfo = self.twitter_auth('/twitterlogin')
        if userInfo:
            user = User.gql('WHERE twitter_id = :1', userInfo['twitter_id']).get()
            if not user:
                user = data_models.register_user(userInfo)
                data_models.store_exinfo(user.user_id, userInfo)
                data_models.update_twitter_info(user, userInfo)
                data_models.update_twitter_friends(user, userInfo)
            else:
                data_models.update_twitter_info(user, userInfo)
                data_models.update_twitter_friends(user, userInfo)
            info = {'uid':user.user_id, 'origin':'twitter', 'origin_id':userInfo['twitter_id']}
            self.set_cookies(info)
            
            self.redirect('/')
            
class FacebookLogin(BasicHandler):
    def get(self):
        userInfo = self.facebook_auth('/facebooklogin')
        if userInfo:
            user = User.gql('WHERE facebook_id = :1', userInfo['facebook_id']).get()
            if not user:
                user = data_models.register_user(userInfo)
                data_models.store_exinfo(user.user_id, userInfo)
                data_models.update_facebook_info(user, userInfo)
                data_models.update_facebook_friends(user, userInfo)
            else:
                data_models.update_facebook_info(user, userInfo)
                data_models.update_facebook_friends(user, userInfo)
    
            info = {'uid':user.user_id, 'origin':'facebook', 'origin_id':userInfo['facebook_id']}
            self.set_cookies(info)
                
            self.redirect('/')

class LinkedInLogin(BasicHandler):
    def get(self):
        userInfo = self.facebook_auth('/linkedinlogin')
        if userInfo:
            user = User.gql('WHERE linkedin_id = :1', userInfo['linkedin_id']).get()
            if not user:
                user = data_models.register_user(userInfo)
                data_models.store_exinfo(user.user_id, userInfo)
                data_models.update_facebook_info(user, userInfo)
                data_models.update_facebook_friends(user, userInfo)
            else:
                data_models.update_facebook_info(user, userInfo)
                data_models.update_facebook_friends(user, userInfo)
    
            info = {'uid':user.user_id, 'origin':'linkedin', 'origin_id':userInfo['linkedin_id']}
            self.set_cookies(info)
                
            self.redirect('/')
        
class CrediblewebLogin(BasicHandler):
    def post(self):
        email = self.request.get('email')
        password = self.request.get('password')
        user = User.gql('WHERE email = :1', email).get()
        if not user:
            error = "User doesn't exist!"
            self.render('welcome.html',
                        login_error = error)
            return
        if user.password != hashlib.sha1(password).hexdigest():
            error = "Wrong Password!"
            self.render('welcome.html',
                        login_error = error)
            return
        info = {'uid':user.user_id, 'origin':'credibleweb'}
        self.set_cookies(info)

        self.redirect('/')


#def cache_user_info(uid, origin, origin_id = None):
#    cache = memcache.Client()
#    cache.add_multi({'uid':uid,
#                     'origin':origin,
#                     'origin_id':origin_id}, 
#                    time = 60)
        

app = webapp2.WSGIApplication([('/twitterlogin', TwitterLogin),
                               ('/facebooklogin', FacebookLogin),
                               ('/credibleweblogin', CrediblewebLogin)],
                              debug=True)