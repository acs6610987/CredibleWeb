from google.appengine.api import memcache

def cache_get(key):
    client = memcache.Client()
    return client.get(key)
    
def cache_put(key, value):
    client = memcache.Client()
    client.set(key, value, time=7200)
    