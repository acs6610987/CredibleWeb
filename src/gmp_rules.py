from data_models import GMPoints, Friends, URLStorage, Rating
import math
import logging
import datetime
import gae_cache

REGISTRATION_POINTS = 5
FRIEND_POINTS = 5
BASIC_RATING_POINTS = 5
SPARSITY_LEVEL = [10, 20, 30, 40, 50, 10000000]
SPARSITY_POINTS = [10, 9, 8, 7, 6, 5]

def rule_registration(user):
    gmp = get_user_gmp(user.user_id)
    gmp.action_points += REGISTRATION_POINTS
    gmp.total_points = gmp.sn_points + gmp.rating_points + gmp.action_points
    gmp.current_points += REGISTRATION_POINTS
    update_user_gmp_cache(user.user_id, gmp)
    gmp.put()
    
def rule_sn_award(user):
    friend_num = Friends.gql('WHERE user_id1 = :1', user.user_id).count()
    gmp = get_user_gmp(user.user_id)
    gmp.current_points += (friend_num * FRIEND_POINTS - gmp.sn_points)
    gmp.sn_points = friend_num * FRIEND_POINTS
    gmp.total_points = gmp.sn_points + gmp.rating_points + gmp.action_points
    update_user_gmp_cache(user.user_id, gmp)
    gmp.put()
    
def rule_rating_award(points, user):
    gmp = get_user_gmp(user.user_id)
    gmp.rating_points += points
    gmp.total_points = gmp.sn_points + gmp.rating_points + gmp.action_points
    gmp.current_points += points
    update_user_gmp_cache(user.user_id, gmp)
    gmp.put()
    
def worth_points(url, user, update_cache = False):
    points = gae_cache.cache_get(user.user_id+url+'points')
    if points and not update_cache:
        return points
    points = None
    
    m_rating = Rating.gql('WHERE user_id = :1 AND url = :2', user.user_id, url).get()
    #if less than one hour between two attempts, no points are awarded
    current_time = datetime.datetime.now()
    if m_rating and (current_time - m_rating.time).total_seconds() < 3600:
        points = 0
    
    if points is None:
        points =  BASIC_RATING_POINTS
        #punish multiple attempts to a specific url
        punish_coefficient = 1
        if m_rating:
            punish_coefficient = math.pow(0.5, float(m_rating.attempts))
        sparse_points = 0
        diff_coefficient = 1
        url_stat = URLStorage.gql('WHERE url = :1', url).get()
        if url_stat:
            for i in range(6):
                if url_stat.total < SPARSITY_LEVEL[i]:
                    sparse_points = SPARSITY_POINTS[i]
                    break
            r = url_stat.ratings
            diff_coefficient = 1.0 / (((abs(r[4] + r[3] - r[1] - r[0])) / (r[4] + r[3] + r[1] + r[0] + 10.0)) + 1)
            points = int(math.ceil(sparse_points * diff_coefficient * punish_coefficient))
    
    gae_cache.cache_put(user.user_id+url+'points', points)
    return points

def get_user_gmp(user_id):
    gmp = gae_cache.cache_get(user_id+'gmp')
    if gmp :
        return gmp
    gmp = GMPoints.gql('WHERE user_id = :1', user_id).get()
    gae_cache.cache_put(user_id+'gmp', gmp)
    return gmp

def update_user_gmp_cache(user_id, gmp):
    gae_cache.cache_put(user_id+'gmp', gmp)
    
        
    
        
            