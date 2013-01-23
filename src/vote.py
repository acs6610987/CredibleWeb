import webapp2
from basichandler import BasicHandler
from data_models import Vote, Rating

class VoteHandler(BasicHandler):
    def get(self):
        rid = self.request.get('rid')
        vote = Vote.gql('WHERE user_id = :1 AND rating_id = :2', self.user.user_id, rid).get()
        if vote:
            self.response.out.write('0')
        else:
            vote = Vote(user_id = self.user.user_id,
                        rating_id = rid)
            review = Rating.get_by_key_name(rid)
            review.upvotes += 1
            review.put()
            vote.put()
            self.response.out.write('1')

app = webapp2.WSGIApplication([('/vote', VoteHandler)], 
                              debug = True)
        