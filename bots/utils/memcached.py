from constants import MEMCACHED_URL
import memcache

class Memcached(object):

    memcached_instance = None

    @staticmethod
    def get_instance():
        """Returns a memcached client instance"""
        if Memcached.memcached_instance is None:
            Memcached.memcached_instance = memcache.Client([MEMCACHED_URL], cache_cas=True)

        return Memcached.memcached_instance


    @staticmethod
    def add(key, value):
        Memcached.get_instance().set(key, value)


    @staticmethod
    def get(key):
        return Memcached.get_instance().get(key)


    @staticmethod
    def delete(key):
        Memcached.get_instance().delete(key)
