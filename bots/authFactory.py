import tweepy
from secrets import *

class AuthFactory(object):
    """
    This class manages the Twitter authentication process
    """
    _instance = None
    _auth = None
    _api = None

    def __new__(self):
        if not AuthFactory._instance:
            AuthFactory._instance = super(AuthFactory, self).__new__(self)

        if not AuthFactory._auth:
            AuthFactory._auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            AuthFactory._auth.set_access_token(access_token, access_token_secret)
            AuthFactory._api = tweepy.API(AuthFactory._auth)

        return AuthFactory._instance


    def get_api(self):
        return AuthFactory._api

    def get_authentication(self):
        return AuthFactory._auth
