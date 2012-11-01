from data_models import URLStorage
from google.appengine.ext.db import stats
from google.appengine.ext import db
import logging

def test_import():
#    data = [('Celebrities', 'http://www.adamofficial.com/us/intro', 1),
#            ('Celebrities', 'http://www.blippitt.com/adam-lambert-album-cover', 2),
#            ('Environment', 'http://www.businessweek.com/blogs/money_politics/archives/2009/06/house_passes_ca.html', 3),
#            ('Environment', 'http://topics.politico.com/index.cfm/topic/CapAndTrade', 4),
#            ('Health', 'http://www.guardian.co.uk/science/2009/sep/06/alzheimers-disease-genes-research', 5),
#            ('Health',  "http://alzheimers.emedtv.com/alzheimer's-disease/alzheimer's-and-genes.html", 6),
#            ('Personal Finance', 'http://www.ehow.com/how_2291042_reduce-credit-card-debt.html', 7),
#            ('Personal Finance', 'http://personal-debt-management.suite101.com/article.cfm/reduce_debt', 8),
#            ('Politics', 'http://michellemalkin.com/2009/08/09/death-panels-what-death-panels-oh-those-death-panels/', 9),
#            ('Politics', 'http://abcnews.go.com/Politics/story?id=8298267&page=1', 10)]
#    for item in data:
#        url = URLStorage(topic = item[0],
#                         url = item[1],
#                         index = item[2])
#        url.put()
    m_stat = stats.KindStat.gql('WHERE kind_name = :1', 'URLStorage').get()
    logging.info(m_stat.count)
    