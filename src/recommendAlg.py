from google.appengine.ext.db import stats
import random
from data_models import URLStorage

URL_COUNT = 1000
def randomAlg(num = 10):
#    m_stat = stats.KindStat.gql('WHERE kind_name = :1', 'URLStorage').get()
    li = [random.randint(1, URL_COUNT) for i in range(num)]
    query = URLStorage.gql('WHERE index IN :1', li)
    recommendations = [item for item in query]
    return recommendations
    
