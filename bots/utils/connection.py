from pymongo import MongoClient
from utils.constants import MONGODB_HOST, MONGODB_PORT, MONGODB_DATABASE, MONGODB_USERNAME, MONGODB_PASSWORD


class MongoConnection(object):

    _instance = None

    class Mongo:
        def __init__(self, connection):
            self.connection = connection

        def get_database(self):
            return self.connection[MONGODB_DATABASE]

    def __init__(self):
        if MongoConnection._instance is None:
            connection_string = 'mongodb://' + MONGODB_USERNAME + ':' + MONGODB_PASSWORD + '@' \
                                + MONGODB_HOST + ':' + str(MONGODB_PORT) # + '/' + MONGODB_DATABASE

            connection = MongoClient(connection_string)
            MongoConnection._instance = MongoConnection.Mongo(connection)

    def __getattr__(self, item):
        return getattr(MongoConnection._instance, item)

    def __set__(self, name, value):
        return setattr(self._instance, name, value)