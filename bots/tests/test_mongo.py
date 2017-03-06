import unittest
from utils.connection import MongoConnection


class TestMongo(unittest.TestCase):
    """python -m unittest tests.test_mongo"""

    def __init__(self, *args, **kwargs):
        super(TestMongo, self).__init__(*args, **kwargs)

    def setUp(self):
        self.mongoclient = MongoConnection()

    def test_connection_works(self):
        db = self.mongoclient.get_database()
        self.assertIsNotNone(db)
        self.assertIsNotNone(self.mongoclient.connection.server_info())

if __name__=='__main__':
    unittest.main()

