from google.appengine.ext import db, ndb
from google.appengine.api import urlfetch
#from google.appengine.api import background_thread
import thread
import conf
import random
import logging
import urllib
import json
import urllib2
import re

EXPERTISES = {'arts_entertainment':'Arts & Entertainment',
             'health':'Health',
             'business':'Business',
             'computer_internet':'Computer & Internet',
             'religion':'Religion',
             'sports':'Sports',
             'culture_politics':'Culture & Politics',
             'gaming':'Gaming',
             'weather':'Weather',
             'science_technology':'Science & Technology',
             'law_crime':'Law & Crime',
             'recreation':'Recreation',
             'unknown_category':'Unknown Category'}
LogScale = 10
OverallStatus = {'Novice':0,
                 'Beginner':10,
                 'Enthusiast':100,
                 'Expert':1000,
                 'Master':10000}
LevelHeight = 13
MaxHeight = 60


class User(db.Model):
    user_id = db.StringProperty(required = True)
    firstname = db.StringProperty()
    lastname = db.StringProperty()
    realname = db.StringProperty()
    email = db.StringProperty()
    picture = db.StringProperty()
    password = db.StringProperty()
    facebook_id = db.StringProperty()
    twitter_id = db.StringProperty()
    fb_access_token = db.StringProperty()
    tw_access_token = db.StringProperty()
    tw_token_secret = db.StringProperty()
    
class ExUserInfo(db.Model):
    user_id = db.StringProperty(required = True)
    website = db.StringProperty()
    location = db.StringProperty()
    photo = db.BlobProperty()
    expertise = db.StringListProperty()
    
class FacebookProfile(db.Model):
    facebook_id = db.StringProperty(required = True)
    realname = db.StringProperty()
    username = db.StringProperty()
    picture = db.StringProperty()
    location = db.StringProperty()
    website = db.StringProperty()

class TwitterProfile(db.Model):
    twitter_id = db.StringProperty(required = True)
    realname = db.StringProperty()
    username = db.StringProperty()
    picture = db.StringProperty()
    location = db.StringProperty()
    website = db.StringProperty()

#need to update in merge if change this to undirected
class Friends(db.Model):
    user_id1 = db.StringProperty(required = True)
    user_id2 = db.StringProperty(required = True)
    
class FBFriends(db.Model):
    facebook_id = db.StringProperty(required = True)
    friends = db.StringListProperty()
    num_on_cw = db.IntegerProperty()

class TWFriends(db.Model):
    twitter_id = db.StringProperty(required = True)
    friends = db.StringListProperty()
    num_on_cw = db.IntegerProperty()
    
class Rating(db.Model):
    rating_id = db.StringProperty(required = True)
    user_id = db.StringProperty(required = True)
    url = db.StringProperty(required = True)
    rating = db.IntegerProperty(required = True)
    comment = db.StringProperty()
    time = db.DateTimeProperty(auto_now = True)
    attempts = db.IntegerProperty()
    truthfulness = db.IntegerProperty()
    unbiased = db.IntegerProperty()
    security = db.IntegerProperty()
    design = db.IntegerProperty()
    upvotes = db.IntegerProperty()
    
class Vote(db.Model):
    user_id = db.StringProperty(required = True)
    rating_id = db.StringProperty(required = True)
    
class Feedback(db.Model):
    type = db.StringProperty(required = True)
    description = db.TextProperty(required = True)
    name = db.StringProperty()
    browser = db.StringProperty()
    email = db.StringProperty()

#class URLStorage(ndb.Model):
#    topic = ndb.StringProperty()
#    url = ndb.StringProperty()
#    index = ndb.IntegerProperty()
#    ratings = ndb.IntegerProperty(repeated = True)
#    total = ndb.IntegerProperty()
#    snapshot = ndb.StringProperty()
#    title = ndb.StringProperty()
#    diff_coefficient = ndb.FloatProperty() #smaller value means a higher disagreement
    
class URLStorage(db.Model):
    topic = db.StringProperty()
    url = db.StringProperty()
    index = db.IntegerProperty()
    ratings = db.ListProperty(int)
    total = db.IntegerProperty()
    snapshot = db.StringProperty()
    title = db.StringProperty()
    diff_coefficient = db.FloatProperty() #smaller value means a higher disagreement
    
class SnapshotStorage(db.Model):
    url = db.StringProperty()
    snapshot = db.BlobProperty()
    
class TestURLStorage(db.Model):
    topic = db.StringProperty()
    url = db.StringProperty()
    index = db.IntegerProperty()
    ratings = db.ListProperty(int)
    total = db.IntegerProperty()
    snapshot = db.StringProperty()
    title = db.StringProperty()
    diff_coefficient = db.FloatProperty()
    
#need to process during merge
class GMPoints(db.Model):
    user_id = db.StringProperty(required = True)
    sn_points = db.IntegerProperty()
    rating_points = db.IntegerProperty()
    action_points = db.IntegerProperty()
    total_points = db.IntegerProperty()
    current_points = db.IntegerProperty()
    
#need to process during merge
class PendingRequest(db.Model):
    sender_id = db.StringProperty(required = True)
    receiver_id = db.StringProperty(required = True)
    
class Statistics(db.Model):
    url_count = db.IntegerProperty()
    
    
def generate_uid():
    uid = ''.join([str(random.randint(0, 9)) for i in range(conf.UID_LEN)])
    while User.get_by_key_name(uid):
        uid = ''.join([str(random.randint(0, 9)) for i in range(conf.UID_LEN)])
    return uid

def generate_rid():
    rid = ''.join([str(random.randint(0, 9)) for i in range(conf.RID_LEN)])
    while Rating.get_by_key_name(rid):
        rid = ''.join([str(random.randint(0, 9)) for i in range(conf.RID_LEN)])
    return rid

def register_user(info):
    uid = generate_uid()
    user = User(key_name = uid,
                user_id = uid,
                firstname = info.get('firstname') or '',
                lastname = info.get('lastname') or '',
                realname = info.get('realname') or '',
                email = info.get('email') or '',
                picture = info.get('picture') or '',
                facebook_id = info.get('facebook_id'),
                twitter_id = info.get('twitter_id'),
                fb_access_token = info.get('fb_access_token'),
                tw_access_token = info.get('tw_access_token'),
                tw_token_secret = info.get('tw_token_secret'),
                password = info.get('password'))
    user.put()
    
#    import gmp_rules
    gmp = GMPoints(user_id = uid,
                   sn_points = 0,
                   rating_points = 0,
                   action_points = 5,
                   total_points = 5,
                   current_points = 5)
    gmp.put()
    
    return user

def store_exinfo(uid, info):
    ex = ExUserInfo.get_by_key_name(uid)
    if not ex:
        ex = ExUserInfo(key_name = uid, user_id = uid)
    ex.website = info.get('website') or ''
    ex.location = info.get('location') or ''
    ex.expertise = info.get('expertise') or []
    ex.put()

def update_facebook_info(user, info):
    new_token = info.get('fb_access_token')
    if new_token and new_token != user.fb_access_token:
        user.fb_access_token = new_token
        user.put()
    
    fbuser = FacebookProfile.gql('WHERE facebook_id = :1', info['facebook_id']).get()
    if not fbuser:
        fbuser = FacebookProfile(facebook_id = info['facebook_id'])
    fbuser.realname = info.get('realname') or ''
    fbuser.username = info.get('username') or ''
    fbuser.picture = info.get('picture') or ''
    fbuser.location = info.get('location') or ''
    fbuser.website = info.get('website') or ''
    fbuser.put()
    

def update_twitter_info(user, info):
    new_token = info.get('tw_access_token')
    new_token_secret = info.get('tw_token_secret')
    if new_token and new_token != user.tw_access_token:
        user.tw_access_token = new_token
        user.tw_token_secret = new_token_secret
        user.put()
    
    twuser = TwitterProfile.gql('WHERE twitter_id = :1', info['twitter_id']).get()
    if not twuser:
        twuser = TwitterProfile(twitter_id = info['twitter_id'])
    twuser.realname = info.get('realname') or ''
    twuser.username = info.get('username') or ''
    twuser.picture = info.get('picture') or ''
    twuser.location = info.get('location') or ''
    twuser.website = info.get('website') or ''
    twuser.put()
    
def update_facebook_friends(user, info):
    fbuser = FBFriends.gql('WHERE facebook_id = :1', info.get('facebook_id')).get()
    if not fbuser:
        fbuser = FBFriends(facebook_id = info.get('facebook_id'))
    friends = info.get('friends')
    friends = set(friends)
    query = User.all()
    cw_fb_ids = [item.facebook_id for item in query]
    fb_on_cw = list(friends.intersection(cw_fb_ids))
    fbuser.num_on_cw = len(fb_on_cw)
    
    friends.difference_update(fb_on_cw)
    realign_friends = list(fb_on_cw)
    realign_friends.extend(friends)
    fbuser.friends = realign_friends
    fbuser.put()
    
    for fb_id in fb_on_cw:
        tmpuser = User.gql('WHERE facebook_id = :1', fb_id).get()
        relation = Friends.gql('WHERE user_id1 = :1 AND user_id2 = :2', user.user_id, tmpuser.user_id).get()
        if not relation:
            relation1 = Friends(user_id1 = user.user_id,
                                user_id2 = tmpuser.user_id)
            relation1.put()
            relation2 = Friends(user_id1 = tmpuser.user_id,
                                user_id2 = user.user_id)
            relation2.put()
    
    import gmp_rules
    gmp_rules.rule_sn_award(user)
    
    
def update_twitter_friends(user, info):
    twuser = TWFriends.gql('WHERE twitter_id = :1', info.get('twitter_id')).get()
    if not twuser:
        twuser = TWFriends(twitter_id = info.get('twitter_id'))
    friends = info.get('friends')
    friends = set(friends)
    query = User.all()
    cw_tw_ids = [item.twitter_id for item in query]
    tw_on_cw = list(friends.intersection(cw_tw_ids))
    twuser.num_on_cw = len(tw_on_cw)
    
    friends.difference_update(tw_on_cw)
    realign_friends = list(tw_on_cw)
    realign_friends.extend(friends)
    twuser.friends = realign_friends
    twuser.put()
    
    for tw_id in tw_on_cw:
        tmpuser = User.gql('WHERE twitter_id = :1', tw_id).get()
        relation = Friends.gql('WHERE user_id1 = :1 AND user_id2 = :2', user.user_id, tmpuser.user_id).get()
        if not relation:
            relation1 = Friends(user_id1 = user.user_id,
                                user_id2 = tmpuser.user_id)
            relation1.put()
            relation2 = Friends(user_id1 = tmpuser.user_id,
                                user_id2 = user.user_id)
            relation2.put()
    
    import gmp_rules
    gmp_rules.rule_sn_award(user)

def merge_facebook(user, facebook_info):
    update_facebook_info(user, facebook_info)
    merge_user = User.gql('WHERE facebook_id = :1', facebook_info['facebook_id']).get()
    if merge_user:
        if user.user_id == merge_user.user_id:
            return "Already Merged!"
        if merge_user.twitter_id:
            user.twitter_id = merge_user.twitter_id
            user.tw_access_token = merge_user.tw_access_token
            user.tw_token_secret = merge_user.tw_token_secret
        
#        query = db.GqlQuery('SELECT url FROM Rating WHERE user_id = :1', user.user_id)
#        url_list = [item.url for item in query]
#        query = Rating.gql('WHERE user_id = :1 AND url IN :2', merge_user.user_id, url_list)
#        for rating in query:
#            rating.delete()
        query = Rating.gql('WHERE user_id = :1', merge_user.user_id)
        for rating in query:
            rating.user_id = user.user_id
            rating.put()
            
        query = Friends.gql('WHERE user_id1 = :1', merge_user.user_id)
        for relation in query:
            if relation.user_id2 == user.user_id:
                relation.delete()
                continue
            relation.user_id1 = user.user_id
            relation.put()
        query = Friends.gql('WHERE user_id2 = :1', merge_user.user_id)
        for relation in query:
            if relation.user_id1 == user.user_id:
                relation.delete()
                continue
            relation.user_id2 = user.user_id
            relation.put()
            
        exInfo1 = ExUserInfo.gql('WHERE user_id = :1', user.user_id).get()
        exInfo2 = ExUserInfo.gql('WHERE user_id = :1', merge_user.user_id).get()
        exInfo1.website = exInfo1.website or exInfo2.website
        exInfo1.location = exInfo1.location or exInfo2.location
        exInfo1.photo = exInfo1.photo or exInfo2.photo
        exInfo1.expertise = exInfo1.expertise or exInfo2.expertise
        exInfo1.put()
        exInfo2.delete()
        
        gmp1 = GMPoints.gql('WHERE user_id = :1', user.user_id).get()
        gmp2 = GMPoints.gql('WHERE user_id = :1', merge_user.user_id).get()
        gmp1.sn_points += gmp2.sn_points
        gmp1.action_points += gmp2.action_points
        gmp1.rating_points += gmp2.rating_points
        gmp1.total_points += gmp2.total_points
        gmp1.current_points += gmp2.current_points
        gmp1.put()
        gmp2.delete()
        
        query = PendingRequest.gql('WHERE sender_id = :1', merge_user.user_id)
        for req in query:
            req.sender_id = user.user_id
            req.put()
        query = PendingRequest.gql('WHERE receiver_id = :1', merge_user.user_id)
        for req in query:
            req.receiver_id = user.user_id
            req.put()
        
        merge_user.delete()
    user.facebook_id = facebook_info['facebook_id']
    user.put()
    return 'Successfully Merged!'
        
def merge_twitter(user, twitter_info):
    update_twitter_info(user, twitter_info)
    merge_user = User.gql('WHERE twitter_id = :1', twitter_info['twitter_id']).get()
    if merge_user:
        if user.user_id == merge_user.user_id:
            return "Already Merged!"
        if merge_user.facebook_id:
            user.facebook_id = merge_user.facebook_id
            user.fb_access_token = merge_user.fb_access_token
        
#        query = db.GqlQuery('SELECT url FROM Rating WHERE user_id = :1', user.user_id)
#        url_list = [item.url for item in query]
#        query = Rating.gql('WHERE user_id = :1 AND url IN :2', merge_user.user_id, url_list)
#        for rating in query:
#            rating.delete()
        query = Rating.gql('WHERE user_id = :1', merge_user.user_id)
        for rating in query:
            rating.user_id = user.user_id
            rating.put()
            
        query = Friends.gql('WHERE user_id1 = :1', merge_user.user_id)
        for relation in query:
            if relation.user_id2 == user.user_id:
                relation.delete()
                continue
            relation.user_id1 = user.user_id
            relation.put()
        query = Friends.gql('WHERE user_id2 = :1', merge_user.user_id)
        for relation in query:
            if relation.user_id1 == user.user_id:
                relation.delete()
                continue
            relation.user_id2 = user.user_id
            relation.put()
            
        exInfo1 = ExUserInfo.gql('WHERE user_id = :1', user.user_id).get()
        exInfo2 = ExUserInfo.gql('WHERE user_id = :1', merge_user.user_id).get()
        exInfo1.website = exInfo1.website or exInfo2.website
        exInfo1.location = exInfo1.location or exInfo2.location
        exInfo1.photo = exInfo1.photo or exInfo2.photo
        exInfo1.expertise = exInfo1.expertise or exInfo2.expertise
        exInfo2.delete()
        
        gmp1 = GMPoints.gql('WHERE user_id = :1', user.user_id).get()
        gmp2 = GMPoints.gql('WHERE user_id = :1', merge_user.user_id).get()
        gmp1.sn_points += gmp2.sn_points
        gmp1.action_points += gmp2.action_points
        gmp1.rating_points += gmp2.rating_points
        gmp1.total_points += gmp2.total_points
        gmp1.current_points += gmp2.current_points
        gmp1.put()
        gmp2.delete()
        
        query = PendingRequest.gql('WHERE sender_id = :1', merge_user.user_id)
        for req in query:
            req.sender_id = user.user_id
            req.put()
        query = PendingRequest.gql('WHERE receiver_id = :1', merge_user.user_id)
        for req in query:
            req.receiver_id = user.user_id
            req.put()
            
        merge_user.delete()
    user.twitter_id = twitter_info['twitter_id']
    user.put()
    return 'Successfully Merged!'

def get_stat():
    stat = Statistics.all()
    if stat.count() > 0:
        return stat.get()
    url_count = URLStorage.all().count()
    stat = Statistics(url_count = url_count)
    stat.put()
    return stat

def update_url_storage(url, oldrating, newrating):
    url_rec = URLStorage.gql('WHERE url = :1', url).get()
    stat = get_stat()
    if url_rec:
        if oldrating:
            #eliminate the previous record
            url_rec.ratings[oldrating-1] -= 1
            url_rec.total -= 1
        url_rec.ratings[newrating-1] += 1
        url_rec.total += 1
        url_rec.put()
    else:
        # need to use AlchemyAPI to compute the topic
        url_rec = URLStorage(topic = 'unknown_category',
                             url = url,
                             title = url,
                             index = stat.url_count + 1,
                             ratings = [0,0,0,0,0],
                             total = 1)
        url_rec.ratings[newrating-1] += 1
        url_rec.put()
        stat.url_count += 1
        stat.put()
        download_info(url_rec)
    update_url_diff(url_rec = url_rec)
    
def test_update_url_storage(url, oldrating, newrating):
    url_rec = TestURLStorage.gql('WHERE url = :1', url).get()
    if url_rec:
        if oldrating:
            #eliminate the previous record
            url_rec.ratings[oldrating-1] -= 1
            url_rec.total -= 1
        url_rec.ratings[newrating-1] += 1
        url_rec.total += 1
        url_rec.put()
    else:
        # need to use AlchemyAPI to compute the topic
        url_rec = TestURLStorage(topic = '',
                             url = url,
                             index = 1,
                             ratings = [0,0,0,0,0],
                             total = 1)
        url_rec.ratings[newrating-1] += 1
        url_rec.put()
        download_info(url_rec)
    
def update_url_diff(url=None, url_rec=None):
    if url_rec == None:
        if url == None:
            return
        url_rec = URLStorage.gql('WHERE url = :1', url).get()
        if not url_rec:
            return
    ratings = url_rec.ratings
    total = url_rec.total
    c1 = abs(ratings[0]+ratings[1]+ratings[2]-ratings[3]-ratings[4])
    c2 = abs(ratings[2]+ratings[3]+ratings[4]-ratings[0]-ratings[1])
    c = ((c1+c2)/2.0 + 1)/(total + 10)
    if total > 60:
        url_rec.diff_coefficient = 1
    else:
        url_rec.diff_coefficient = c
    url_rec.put()
    
def download_info(url_rec):
    import tasks
    tasks.addUrlDownloadTask(url_rec)

    