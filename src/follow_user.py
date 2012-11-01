import webapp2
from basichandler import BasicHandler
from data_models import Friends

class FollowHandler(BasicHandler):
    def get(self):
        if self.user:
            uid = self.request.get('uid')
            follow = self.request.get('follow')
            if follow == 'true':
                self.add_following(uid)
            elif follow == 'false':
                self.cancel_following(uid)
        else:
            self.redirect('/')
            
    def add_following(self, uid):
        relationship = Friends.gql('WHERE user_id1 = :1 AND user_id2 = :2', self.user.user_id, uid).get()
        if not relationship:
            relationship = Friends(user_id1 = self.user.user_id,
                                   user_id2 = uid)
            relationship.put()
    
    def cancel_following(self, uid):
        relationship = Friends.gql('WHERE user_id1 = :1 AND user_id2 = :2', self.user.user_id, uid).get()
        if relationship:
            relationship.delete()

app = webapp2.WSGIApplication([('/followuser', FollowHandler)], 
                              debug = True)