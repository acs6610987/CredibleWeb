from data_models import URLStorage
from google.appengine.ext.db import stats
from google.appengine.ext import db
import logging
from csv import DictReader
import data_models

def test_import():
    all = URLStorage.all()
#    db.delete(all)
#    m_reader = DictReader(open('local_data.csv'))
#    for row in m_reader:
#        url = URLStorage(topic = row['topic'],
#                         url = row['url'],
#                         index = int(row['index']),
#                         ratings = [int(r) for r in row['ratings'].split(',')],
#                         total = int(row['total']),
#                         snapshot = row['snapshot'],
#                         title = row['title'].decode('utf-8'))
#        url.put()
#    data = [('Celebrities', 'http://www.adamofficial.com/us/intro', 1, [0, 0, 0, 0,0], 0),
#            ('Celebrities', 'http://www.blippitt.com/adam-lambert-album-cover', 2, [0, 0, 0, 0,0], 0),
#            ('Environment', 'http://www.businessweek.com/blogs/money_politics/archives/2009/06/house_passes_ca.html', 3, [0, 0, 0, 0,0], 0),
#            ('Environment', 'http://topics.politico.com/index.cfm/topic/CapAndTrade', 4, [0, 0, 0, 0,0], 0),
#            ('Health', 'http://www.guardian.co.uk/science/2009/sep/06/alzheimers-disease-genes-research', 5, [0, 0, 0, 0,0], 0),
#            ('Health',  "http://alzheimers.emedtv.com/alzheimer's-disease/alzheimer's-and-genes.html", 6, [0, 0, 0, 0,0], 0),
#            ('Personal Finance', 'http://www.ehow.com/how_2291042_reduce-credit-card-debt.html', 7,[0, 0, 0, 0,0], 0),
#            ('Personal Finance', 'http://personal-debt-management.suite101.com/article.cfm/reduce_debt', 8,[0, 0, 0, 0,0], 0),
#            ('Politics', 'http://michellemalkin.com/2009/08/09/death-panels-what-death-panels-oh-those-death-panels/', 9,[0, 0, 0, 0,0], 0),
#            ('Politics', 'http://abcnews.go.com/Politics/story?id=8298267&page=1', 10,[0, 0, 0, 0,0], 0)]
#    for item in data:
#        url = URLStorage(topic = item[0],
#                         url = item[1],
#                         index = item[2],
#                         ratings = item[3],
#                         total = item[4])
#        url.put()
#    m_stat = stats.KindStat.gql('WHERE kind_name = :1', 'URLStorage').get()

def compute_diff():
    urls = URLStorage.all()
    for url_rec in urls:
        data_models.update_url_diff(url_rec = url_rec)