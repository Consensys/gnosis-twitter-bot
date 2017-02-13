import unittest
from utils.memcached import Memcached


class TestMemcached(unittest.TestCase):
    """python -m unittest tests.test_memcached"""

    def __init__(self, *args, **kwargs):
        super(TestMemcached, self).__init__(*args, **kwargs)


    def setUp(self):
        pass


    def test_new_instance(self):
        instance = Memcached.get_instance()
        self.assertIsNotNone(instance)


    def test_add_method(self):
        Memcached.add("user", "giacomo")
        instance = Memcached.get_instance()
        self.assertEquals(instance.get("user"), "giacomo")


    def test_get_method(self):
        self.assertEquals(Memcached.get("user"), "giacomo")


    def test_delete_method(self):
        Memcached.add("city", "milano")
        self.assertEquals(Memcached.get("city"), "milano")
        Memcached.delete("city")
        self.assertIsNone(Memcached.get("city"))



if __name__=='__main__':
    unittest.main()
