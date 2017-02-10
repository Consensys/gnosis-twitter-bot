from subprocess import Popen, PIPE
import os
import memcache
import json
import tweepy
import time

class PublisherBot(object):
    """Publisher bot class"""

    _instance = None

    # Constants - TODO put them in a common configuration file
    GNOSIS_TWITTER_NAME = '@gnosismarketbot'
    GNOSIS_URL = 'https://beta.gnosis.pm/#/market/'
    MEMCACHE_URL = os.getenv('MEMCACHED_URL', '127.0.0.1:11211')
    MARKET_MANAGER_DIR = '../market-manager/'
    GET_MARKETS_FILE = 'getMarkets.js'
    GET_QR_FILE = 'getQR.js'

    def __init__(self, auth):
        self._auth = auth
        self._actual_market = {}
        self._actual_market_hash = None
        self._markets = []
        self._memcache = memcache.Client([PublisherBot.MEMCACHE_URL], cache_cas=True)

    def __new__(self, auth):
        if auth:
            if not PublisherBot._instance:
                PublisherBot._instance = super(PublisherBot, self).__new__(self, auth)

            return PublisherBot._instance

        else:
            raise Exception('Authentication not provided')


    def get_markets(self):
        markets = []

        try:
            process = Popen(["node", PublisherBot.MARKET_MANAGER_DIR + PublisherBot.GET_MARKETS_FILE, "."], stdout=PIPE, stderr=PIPE)
            (output, err) = process.communicate()
            exit_code = process.wait()
            markets = json.loads(output)

            if err:
                pass #TODO define what to do with returning errors

            return markets

        except (ValueError, KeyError, TypeError):
            raise


    def load_markets(self):
        try:
            self._markets = self.get_markets()

            if len(self._markets) == 0:
                raise Exception('No markets found')

        except Exception:
            raise

        # 1st chech if cache contains the market hash
        if self._memcache.get('market_hash'):

            self._actual_market_hash = self._memcache.get('market_hash')

            # Find the next available market hash
            n_markets = len(self._markets)

            # market_found variable is used to manage 'market not found' cases
            market_found = False

            for x in range(0, n_markets):
                if self._markets[x]['marketHash'] == self._actual_market_hash:
                    market_found = True
                    if x == n_markets-1:
                        self._actual_market = self._markets[0]
                        break
                    else:
                        self._actual_market = self._markets[x+1]
                        break


            if not market_found:
                self._actual_market = self._markets[0]
                self._actual_market_hash = self._actual_market['marketHash']
            else:
                self._actual_market_hash = self._actual_market['marketHash']
        else:
            # Set the first element of the markets array
            # This happens when the publisher is executed for the 1st time
            self._actual_market = self._markets[0]
            self._actual_market_hash = self._actual_market['marketHash']


    def add_to_memcache(self, key, value):
        self._memcache.set(key, value)


    def tweet_new_market(self):
        # get Twitter API instance
        api = self._auth.get_api()
        # marketTitle
        message = self._actual_market['description']['title'] + ' '

        # odds
        if 'outcomes' in self._actual_market['description']:
            # discrete
            message += self._actual_market['description']['outcomes'][0] + ' '
            message += '(' + str(float(self._actual_market['prices'][0])*100) + ' %)'

        else:
            # ranged
            message += ' Current ' + self._actual_market['prices'][0] + ' '
            message += self._actual_market['description']['unit']

        # marketHashAsLink
        message += ' ' + PublisherBot.GNOSIS_URL
        message += self._actual_market['descriptionHash'] + '/'
        message += self._actual_market['marketAddress'] + '/'
        message += self._actual_market['marketHash'] + '?t=' + str(int(time.time()*1000))

        res = api.update_status(message)

        # Set memcache
        self.add_to_memcache('market_hash', self._actual_market_hash)
