from google.appengine.ext import db
import conf
import random

class User(db.Model):
    user_id = db.StringProperty(required = True)
    realname = db.StringProperty()
    username = db.StringProperty()
    picture = db.StringProperty()
    password = db.StringProperty()
    facebook_id = db.StringProperty()
    twitter_id = db.StringProperty()
    fb_access_token = db.StringProperty()
    tw_access_token = db.StringProperty()
    tw_token_secret = db.StringProperty()
    
class ExUserInfo(db.Model):
    user_id = db.StringProperty(required = True)
    email = db.StringProperty()
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

class Friends(db.Model):
    user_id1 = db.StringProperty(required = True)
    user_id2 = db.StringProperty(required = True)
    
class Rating(db.Model):
    user_id = db.StringProperty(required = True)
    url = db.StringProperty(required = True)
    rating = db.IntegerProperty(required = True)
    time = db.DateTimeProperty(auto_now = True)
    
class Feedback(db.Model):
    type = db.StringProperty(required = True)
    description = db.TextProperty(required = True)
    name = db.StringProperty()
    browser = db.StringProperty()
    email = db.StringProperty()

class URLStorage(db.Model):
    topic = db.StringProperty()
    url = db.StringProperty()
    index = db.IntegerProperty()
    
def generate_uid():
    uid = ''.join([str(random.randint(0, 9)) for i in range(conf.UID_LEN)])
    while User.get_by_key_name(uid):
        uid = ''.join([str(random.randint(0, 9)) for i in range(conf.UID_LEN)])
    return uid

def register_user(info):
    uid = generate_uid()
    user = User(key_name = uid,
                user_id = uid,
                realname = info.get('realname') or '',
                username = info.get('username') or '',
                picture = info.get('picture') or '',
                facebook_id = info.get('facebook_id'),
                twitter_id = info.get('twitter_id'),
                fb_access_token = info.get('fb_access_token'),
                tw_access_token = info.get('tw_access_token'),
                tw_token_secret = info.get('tw_token_secret'),
                password = info.get('password'))
    user.put()
    
#    ex = ExUserInfo(key_name = uid,
#                    user_id = uid,
#                    email = info.get('email') or '',
#                    website = info.get('website') or '',
#                    location = info.get('location') or '',
#                    interest = info.get('interest') or [],
#                    expertise = info.get('expertise') or [])
#                    
#    ex.put()
    return user

def store_exinfo(uid, info):
    ex = ExUserInfo.get_by_key_name(uid)
    if not ex:
        ex = ExUserInfo(key_name = uid, user_id = uid)
    ex.email = info.get('email') or ''
    ex.website = info.get('website') or ''
    ex.location = info.get('location') or ''
    ex.expertise = info.get('expertise') or []
                    
    ex.put()

def update_facebook_info(user, info):
    user.fb_access_token = info.get('fb_access_token')
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
    user.tw_access_token = info.get('tw_access_token')
    user.tw_token_secret = info.get('tw_token_secret')
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
        
        query = db.GqlQuery('SELECT url FROM Rating WHERE user_id = :1', user.user_id)
        url_list = [item.url for item in query]
        query = Rating.gql('WHERE user_id = :1 AND url IN :2', merge_user.user_id, url_list)
        for rating in query:
            rating.delete()
        query = Rating.gql('WHERE user_id = :1', merge_user.user_id)
        for rating in query:
            rating.user_id = user.user_id
            rating.put()
            
        query = Friends.gql('WHERE user_id1 = :1', merge_user.user_id)
        for relation in query:
            relation.user_id1 = user.user_id
            relation.put()
        query = Friends.gql('WHERE user_id2 = :1', merge_user.user_id)
        for relation in query:
            relation.user_id2 = user.user_id
            relation.put()
            
        exInfo1 = ExUserInfo.gql('WHERE user_id = :1', user.user_id).get()
        exInfo2 = ExUserInfo.gql('WHERE user_id = :1', merge_user.user_id).get()
        exInfo1.email = exInfo1.email or exInfo2.email
        exInfo1.website = exInfo1.website or exInfo2.website
        exInfo1.location = exInfo1.location or exInfo2.location
        exInfo1.photo = exInfo1.photo or exInfo2.photo
        exInfo1.interest = exInfo1.interest or exInfo2.interest
        exInfo1.expertise = exInfo1.expertise or exInfo2.expertise
        
        exInfo1.put()
        exInfo2.delete()
        
        
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
        
        query = db.GqlQuery('SELECT url FROM Rating WHERE user_id = :1', user.user_id)
        url_list = [item.url for item in query]
        query = Rating.gql('WHERE user_id = :1 AND url IN :2', merge_user.user_id, url_list)
        for rating in query:
            rating.delete()
        query = Rating.gql('WHERE user_id = :1', merge_user.user_id)
        for rating in query:
            rating.user_id = user.user_id
            rating.put()
            
        query = Friends.gql('WHERE user_id1 = :1', merge_user.user_id)
        for relation in query:
            relation.user_id1 = user.user_id
            relation.put()
        query = Friends.gql('WHERE user_id2 = :1', merge_user.user_id)
        for relation in query:
            relation.user_id2 = user.user_id
            relation.put()
            
        exInfo1 = ExUserInfo.gql('WHERE user_id = :1', user.user_id).get()
        exInfo2 = ExUserInfo.gql('WHERE user_id = :1', merge_user.user_id).get()
        exInfo1.email = exInfo1.email or exInfo2.email
        exInfo1.website = exInfo1.website or exInfo2.website
        exInfo1.location = exInfo1.location or exInfo2.location
        exInfo1.photo = exInfo1.photo or exInfo2.photo
        exInfo1.interest = exInfo1.interest or exInfo2.interest
        exInfo1.expertise = exInfo1.expertise or exInfo2.expertise
        exInfo2.delete()
            
        merge_user.delete()
    user.twitter_id = twitter_info['twitter_id']
    user.put()
    return 'Successfully Merged!'