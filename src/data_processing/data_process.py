from csv import DictReader, DictWriter
import csv
import json
import urllib
import urllib2
import time
import httplib
from urlparse import urlparse

def convert_to_standard():
    m_reader = DictReader(open('url_data.csv'))
    m_writer = DictWriter(open('converted_data.csv', 'wb'), ['topic', 'url', 'index', 'ratings', 'total'])
    li = []
    index = 1
    for row in m_reader:
        newrow = {'topic':row['Topic'],
                  'url':row['URL'],
                  'index':index}
        ratings = [0, 0, 0, 0, 0]
        total = 0
        if row['Likert Rating - Microsoft']:
            ratings[int(row['Likert Rating - Microsoft']) - 1] += 1
            total += 1
        if row['Likert Rating - EPFL']:
            if int(row['Likert Rating - EPFL']) == 0:
                continue
            ratings[int(row['Likert Rating - EPFL']) - 1] += 1
            total += 1
        newrow['ratings'] = ','.join([str(r) for r in ratings])
        newrow['total'] = total
        index += 1
        li.append(newrow)
        print newrow
#        print row['Topic']+' '+row['Query'] + ' ' + row['URL'] + ' ' + row['Likert Rating - Microsoft'] + ' ' + row['Likert Rating - EPFL']
    m_writer.writerows(li)
    
def convert_to_alchemy():
    m_reader = DictReader(open('part4.csv'))
    m_writer = DictWriter(open('part4_alchemy.csv', 'wb'), ['topic', 'url', 'index', 'ratings', 'total', 'flag'])
    li = []
    for row in m_reader:
        alchemy_key = '6c15f2ea82b0dab7bc9bbb9cda438933fdc02ea3'
        endpoint = 'http://access.alchemyapi.com/calls/url/URLGetCategory'
        params = {'url':row['url'],
          'apikey':alchemy_key,
          'outputMode':'json'}
        alchemy_call = endpoint+'?'+urllib.urlencode(params)
        response = urllib.urlopen(alchemy_call).read()
        print response
        jresponse = json.loads(response)
        newrow = row
        if jresponse.has_key('category'):
            newrow['topic'] = jresponse['category']
            newrow['flag'] = 1
        else:
            newrow['flag'] = 0
        li.append(newrow)
        time.sleep(0.25)
#        break;
    m_writer.writerows(li)
    
def polish_alchemy():
#    m_reader1 = DictReader(open('part1.csv'))
    m_writer = DictWriter(open('alchemy_data.csv', 'wb'), ['topic', 'url', 'index', 'ratings', 'total'])
    li = []
    index = 1
    i = 1
    while i <= 4:
        m_reader = DictReader(open('part' + str(i) + '_alchemy.csv'))  
        for row in m_reader:
            if row['flag'] == '0':
                continue
            newrow = {'topic':row['topic'],
                      'url':row['url'],
                      'index':index,
                      'ratings':row['ratings'],
                      'total':row['total']}
            li.append(newrow)
            index += 1
        i += 1
    m_writer.writerows(li)
    
def generate_snapshots():
    m_reader = DictReader(open('alchemy_data.csv'))
    count = 1
    for row in m_reader:
        if int(row['index']) in [233]:
            if row['url'].endswith('/'):
                row['url'] = row['url'][:len(row['url'])-1]
            row['url'] = row['url'].replace('=', '%3d')
            row['url'] = row['url'].replace('-', '%2d')
            if row['url'].startswith('https'):
                row['url'] = row['url'][:4] + row['url'][5:]
            print row['url']
            url = 'http://immediatenet.com/t/l3?Size=1024x768&URL='+row['url']
            img = urllib.urlopen(url).read()
            imgfile = open('../static/snapshots/l/url' + row['index'] + '.jpg', 'wb')
            imgfile.write(img)
            imgfile.flush()
            imgfile.close()
            time.sleep(3)
            
def add_snapshot():
    m_reader = DictReader(open('alchemy_data.csv'))
    li = []
    for row in m_reader:
        newrow = row
        newrow['snapshot'] = '/static/snapshots/l/url'+row['index']+'.jpg'
        li.append(newrow)
    m_writer = DictWriter(open('data1.csv', 'wb'), ['topic', 'url', 'index', 'ratings', 'total', 'snapshot'])
    m_writer.writerows(li)
    
def add_title():
    import re
    m_reader = DictReader(open('data2.csv', 'rb'))
    li = []
    for row in m_reader:
#        if row['index'] == '1328':
        newrow = row
        flag = False
        try:
            title = unicode(row['title'], 'utf-8')
        except Exception, e:
            flag = True
        if flag:
            content = ''
            try:
                request = urllib2.Request(row['url'])
                request.add_header('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11')
                opener = urllib2.build_opener()
                conn = opener.open(request)
                content_type = conn.info().get('Content-type')
                charset_i = -1
                if content_type:
                    content_type = content_type.lower()
                    charset_i = content_type.rfind('charset=')
                code = 'utf-8'  #default to utf-8
                if charset_i > 0:
                    code = content_type[charset_i+8:].strip(' "\'')
                print code
                content = conn.read()
            except Exception, e:
                print e
                pass
            m = re.search(r'<title.*?>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            if m:
                newrow['title'] = m.group(1)
                newrow['title'] = newrow['title'].strip()
                newrow['title'] = newrow['title'].replace('\n', ' ')
                try:
                    newrow['title'] = unicode(newrow['title'], code, 'ignore')
                except UnicodeDecodeError, e:
                    newrow['title'] = unicode(row['url'])
                newrow['title'] = newrow['title'].encode('utf-8', 'ignore')
            print newrow['index']
            print code
            print newrow['title']
        li.append(newrow)
    m_writer = DictWriter(open('data3.csv', 'ab'), ['topic', 'url', 'index', 'ratings', 'total', 'snapshot', 'title'])
    m_writer.writerow({'topic':'topic',
                'url':'url',
                'index':'index',
                'ratings':'ratings',
                'total':'total',
                'snapshot':'snapshot',
                'title':'title'})
    m_writer.writerows(li)
    return
    m_reader = DictReader(open('data1.csv'))
    li = []
    for row in m_reader:
#        if int(row['index']) >= 1651 and int(row['index']) <= 1750:
        if int(row['index']) == 433:
            newrow = row
            newrow['title'] = row['url']
            content = ''
            print row['index']
            try:
                request = urllib2.Request(row['url'])
                request.add_header('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11')
                opener = urllib2.build_opener()
                conn = opener.open(request)
                
#                print conn.info()
                #find the encoding format
                content_type = conn.info().get('Content-type')
                charset_i = -1
                if content_type:
                    content_type = content_type.lower()
                    charset_i = content_type.rfind('charset=')
                code = 'utf-8'  #default to utf-8
                if charset_i > 0:
                    code = content_type[charset_i+8:].strip(' "\'')
                print code
    #            else:
    #                match_charset = re.search(r'Content-Type.+?content.+?charset\s*=\s*([\w\d-]+)', page, re.IGNORECASE)
    #                if match_charset:
    #                    code = match_charset.group(1)
                content = conn.read()
            except Exception, e:
                print e
                pass
    #            print content
            m = re.search(r'<title.*?>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            if m:
                newrow['title'] = m.group(1)
                newrow['title'] = newrow['title'].strip()
                newrow['title'] = newrow['title'].replace('\n', ' ')
                try:
    #                    newrow['title'].decode(code, 'ignore')
                    newrow['title'] = unicode(newrow['title'], code, 'ignore')
                except UnicodeDecodeError, e:
                    newrow['title'] = unicode(row['url'])
                print newrow['title']
                newrow['title'] = newrow['title'].encode('utf-8', 'ignore')
            li.append(newrow)
    m_writer = DictWriter(open('testdata.csv', 'ab'), ['topic', 'url', 'index', 'ratings', 'total', 'snapshot', 'title'])
#    m_writer.writerow({'topic':'topic',
#                'url':'url',
#                'index':'index',
#                'ratings':'ratings',
#                'total':'total',
#                'snapshot':'snapshot',
#                'title':'title'})
    m_writer.writerows(li)
    
if __name__ == '__main__':
#    convert_to_standard()
#    convert_to_alchemy()
#    polish_alchemy()
    generate_snapshots()
#    add_snapshot()
#    add_title()
#    s = 'fdsfds'
#    s.decode('latin-1')
#    print type(s)
#    s = (s.encode('utf-8'))
#    print type(s)