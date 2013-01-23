import random
from data_models import URLStorage, Rating, ExUserInfo
import data_models
import logging
from google.appengine.ext import db
import gae_cache

DEF_REC_NUM = 6
def randomAlg(num = DEF_REC_NUM):
#    m_stat = stats.KindStat.gql('WHERE kind_name = :1', 'URLStorage').get()
    m_stat = data_models.get_stat()
    li = [random.randint(1, m_stat.url_count) for i in range(num)]
#    li = [1]
    query = URLStorage.gql('WHERE index IN :1', li)
    recommendations = [item for item in query]
    return recommendations

def diffRecommend(user_id, num = DEF_REC_NUM):
    recommendations = gae_cache.cache_get(user_id+'diffrmd')
    if recommendations:
        return recommendations
    
    query1 = URLStorage.gql('ORDER BY diff_coefficient ASC')
    query2 = Rating.gql('WHERE user_id = :1', user_id)
    rated = [item.url for item in query2]
    recommendations = []
    tmp = 0
    for url_rec in query1:
        tmp += 1
        if url_rec.url not in rated:
            recommendations.append(url_rec)
            if len(recommendations) >= num:
                break
    
    gae_cache.cache_put(user_id+'diffrmd', recommendations)
    return recommendations

def sparseRecommend(user_id, num = DEF_REC_NUM):
    recommendations = gae_cache.cache_get(user_id + 'sparsermd')
    if recommendations:
        return recommendations
    
    query1 = URLStorage.gql('ORDER BY total ASC')
    query2 = Rating.gql('WHERE user_id = :1', user_id)
    rated = [item.url for item in query2]
    recommendations = []
    tmp = 0
    for url_rec in query1:
        tmp += 1
        if url_rec.url not in rated:
            recommendations.append(url_rec)
            if len(recommendations) >= num:
                break
    
    gae_cache.cache_put(user_id+'sparsermd', recommendations)
    return recommendations

def expertiseRecommend(user_id, num = DEF_REC_NUM):
    recommendations = gae_cache.cache_get(user_id + 'expertisermd')
    if recommendations:
        return recommendations
    
    expertise = ExUserInfo.gql('WHERE user_id = :1', user_id).get().expertise
    if not expertise:
        return None
    query1 = URLStorage.gql('WHERE topic IN :1', expertise)
#    url_keys = [item for item in query1.run(keys_only=True)]
#    logging.info('number of expertise rmds: ' + str(len(url_keys)))
#    li = [random.randint(0, len(url_keys)-1) for i in range(2*num)]
    query2 = db.GqlQuery('SELECT url from Rating WHERE user_id = :1', user_id)
    rated = [item.url for item in query2]
    recommendations = []
    for url_rec in query1:
#        url_rec = URLStorage.get(url_keys[i])
        if url_rec.url not in rated:
            recommendations.append(url_rec)
            if len(recommendations) >= num:
                break
            
    gae_cache.cache_put(user_id+'expertisermd', recommendations)
    return recommendations

def boredRecommend(user_id, num = DEF_REC_NUM):
    recommendations = gae_cache.cache_get(user_id + 'boredrmd')
    if recommendations:
        return recommendations
    
    expertise = ExUserInfo.gql('WHERE user_id = :1', user_id).get().expertise
    diff_expertise = set(data_models.EXPERTISES.keys())
    diff_expertise.difference_update(set(expertise))
    
    if not diff_expertise:
        return None
    query1 = URLStorage.gql('WHERE topic IN :1', list(diff_expertise))
#    url_recs = [item for item in query1]
#    logging.info('number of bored rmds: ' + str(len(url_recs)))
#    li = [random.randint(0, len(url_recs)-1) for i in range(2*num)]
    query2 = Rating.gql('WHERE user_id = :1', user_id)
    rated = [item.url for item in query2]
    recommendations = []
    for url_rec in query1:
        if url_rec.url not in rated:
            recommendations.append(url_rec)
            if len(recommendations) >= num:
                break
    
    gae_cache.cache_put(user_id+'boredrmd', recommendations)
    return recommendations