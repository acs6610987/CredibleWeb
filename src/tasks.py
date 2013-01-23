import webapp2
from google.appengine.ext import db
from data_models import URLStorage, SnapshotStorage
import conf
import urllib
from google.appengine.api import urlfetch, taskqueue
import json
import urllib2
import re
import logging

class URLInfoDownloadHandler(webapp2.RequestHandler):
    def post(self):
        key = self.request.get('key')
        def txn():
            rec = URLStorage.get(key)
            if rec:
                rec.topic = self.get_topic(rec.url)
                
                img = self.get_snapshot(rec.url)
                ss = SnapshotStorage(url = rec.url)
                ss.snapshot = db.Blob(img)
                ss.put()
                rec.snapshot = '/img/blob_snapshot?key=%s' % ss.key()
                
                rec.title = self.get_title(rec.url)
                rec.put()
        db.run_in_transaction_options(db.create_transaction_options(xg=True), txn)
        
    def get_topic(self, url):
        params = {'url':url,
                  'apikey':conf.ALCHEMY_KEY,
                  'outputMode':'json'}
        alchemy_call = conf.ALCHEMY_ENDPOINT+'?'+urllib.urlencode(params)
        response = urlfetch.fetch(alchemy_call, deadline=60).content
        jresponse = json.loads(response)
        if jresponse.has_key('category'):
            topic = jresponse['category']
        else:
            topic = 'unknown_category'
        return topic
        
    def get_snapshot(self, url):
        if url.endswith('/'):
                url = url[:len(url)-1]
        url = url.replace('=', '%3d')
        url = url.replace('-', '%2d')
        if url.startswith('https'):
            url = url[:4] + url[5:]
        snapshot = 'http://immediatenet.com/t/l3?Size=1024x768&URL='+url
        img = urlfetch.fetch(snapshot, deadline = 120).content
        return img
    
    def get_title(self, url):
        title = url
        content = ''
        try:
            request = urllib2.Request(url)
            request.add_header('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11')
            opener = urllib2.build_opener()
            conn = opener.open(request)
            content_type = conn.info().get('Content-type')
            charset_i = -1
            if content_type:
                content_type = content_type.lower()
                charset_i = content_type.rfind('charset=')
            code = 'utf-8'  #default to utf-8
            if charset_i > 0:
                code = content_type[charset_i+8:].strip(' "\'')
            content = conn.read()
        except Exception, e:
            pass
        m = re.search(r'<title.*?>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
        if m:
            title = m.group(1)
            title = title.strip()
            title = title.replace('\n', ' ')
            try:
                title = unicode(title, code, 'ignore')
            except UnicodeDecodeError, e:
                title = unicode(url)
        return title

def addUrlDownloadTask(url_rec):
    taskqueue.add(url='/urlInfoDownloadTask', params={'key': url_rec.key()})
    
app = webapp2.WSGIApplication([('/urlInfoDownloadTask', URLInfoDownloadHandler)],
                               debug=True)
