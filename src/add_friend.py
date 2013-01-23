import webapp2
from basichandler import BasicHandler
from data_models import Friends, PendingRequest, User
import logging

class AddFriendRequestHandler(BasicHandler):
    def get(self):
        if self.user:
            uid = self.request.get('uid')
            pending = PendingRequest(sender_id = self.user.user_id,
                                     receiver_id = uid)
            pending.put()
        else:
            self.redirect('/')
            
class AgreeFriendRequestHandler(BasicHandler):
    def get(self):
        uid = self.request.get('uid')
        pending = PendingRequest.gql('WHERE sender_id = :1 AND receiver_id = :2', uid, self.user.user_id).get()
        pending.delete()
        
        friends1 = Friends(user_id1 = uid,
                          user_id2 = self.user.user_id)
        friends1.put()
        friends2 = Friends(user_id1 = self.user.user_id,
                           user_id2 = uid)
        friends2.put()
        
class CheckFriendRequestHandler(BasicHandler):
    def get(self):
        query = PendingRequest.gql('WHERE receiver_id = :1', self.user.user_id)
        pending_uids = [item.sender_id for item in query]
        query = User.gql('WHERE user_id IN :1', pending_uids) #IN may have a problem exceeding 30
        reqs = [user for user in query]
        self.render('friendrequest.html',
                    reqs = reqs)
class IgnoreFriendRequestHandler(BasicHandler):
    def get(self):
        uid = self.request.get('uid')
        pending = PendingRequest.gql('WHERE sender_id = :1 AND receiver_id = :2', uid, self.user.user_id).get()
        pending.delete()

app = webapp2.WSGIApplication([('/addfriendrequest', AddFriendRequestHandler),
                               ('/agreefriendrequest', AgreeFriendRequestHandler),
                               ('/checkfriendrequest', CheckFriendRequestHandler),
                               ('/ignorefriendrequest', IgnoreFriendRequestHandler)], 
                              debug = True)