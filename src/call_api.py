import twitter_oauth
import conf
import urllib
from google.appengine.api import urlfetch
import json
import logging

def twitter_api(method, subUrl, params, token, token_secret):
    if params == None:
        params = {}
    oauth_header = twitter_oauth.get_oauth_header(method, 
                                                  conf.TWITTER_API + subUrl,
                                                  params, None,
                                                  conf.TWITTER_CONSUMER_KEY,
                                                  conf.TWITTER_CONSUMER_SECRET,
                                                  token,
                                                  token_secret)
    payload = urllib.urlencode(params)
    if method.upper() == 'GET':
        if payload:
            subUrl += '?' + payload
        response = urlfetch.fetch(conf.TWITTER_API + subUrl,
                                  headers={u'Authorization':oauth_header}).content
    elif method.upper() == 'POST':
        response = urlfetch.fetch(conf.TWITTER_API + subUrl,
                                  payload = payload,
                                  headers={u'Authorization':oauth_header,
                                           u'Content-Type': u'application/x-www-form-urlencoded'}).content
    return json.loads(response)

#remember to put a '/' before your subUrl, because urlfetch won't do that for you, and it may cause an error for a request
def facebook_api(method, subUrl, params):
    if params == None:
        params = {}
    payload = urllib.urlencode(params)
    if method.upper() == 'GET':
        if payload:
            subUrl += '?' + payload
        response = urlfetch.fetch(conf.FACEBOOK_API + subUrl).content
    elif method.upper() == 'POST':
        response = urlfetch.fetch(conf.FACEBOOK_API + subUrl,
                                  payload = payload,
                                  headers={u'Content-Type':u'application/x-www-form-urlencoded'}).content
    return json.loads(response)