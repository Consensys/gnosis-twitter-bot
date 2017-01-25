from subprocess import Popen, PIPE
import memcache
import json
import tweepy

class PublisherBot(object):
    """Publisher bot class"""

    _instance = None

    GNOSIS_URL = 'https://beta.gnosis.pm/'
    MEMCACHE_URL = '127.0.0.1:11211'

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

    def load_markets(self):
        try:
            process = Popen(["node", "../market-manager/index.js", "."], stdout=PIPE)
            (output, err) = process.communicate()
            exit_code = process.wait()

            self._markets = json.loads(output)

            if len(self._markets) == 0:
                raise Exception('No markets found')

            print "markets loaded"

            if err:
                pass #TODO define what to do with returning errors

        except Exception:
            raise

        # 1st chech if cache contains the market hash
        if self._memcache.get('market_hash'):

            self._actual_market_hash = self._memcache.get('market_hash')

            # Find the next available market hash
            n_markets = len(self._markets)

            for x in range(0, n_markets):
                if self._markets[x]['marketHash'] == self._actual_market_hash:
                    if x == n_markets-1:
                        self._actual_market = self._markets[0]
                        break
                    else:
                        self._actual_market = self._markets[x+1]
                        break                        

            self._actual_market_hash = self._actual_market['marketHash']
            # Set memcache
            #self._memcache.set('market_hash', self._actual_market_hash)
        else:
            # Set the first element of the markets array
            self._actual_market = self._markets[0]
            self._actual_market_hash = self._actual_market['marketHash']
            # Set memcache
            #self._memcache.set('market_hash', self._actual_market_hash)

    def add_to_memcache(self, key, value):
        self._memcache.set(key, value)

    def tweet_new_market(self):
        # get Twitter API instance
        api = self._auth.get_api()
        # marketTitle
        message = self._actual_market['description']['description']
        # marketHashAsLink
        message += ' ' + PublisherBot.GNOSIS_URL + '#/market/'
        message += self._actual_market['descriptionHash'] + '/'
        message += self._actual_market['marketAddress'] + '/'
        message += self._actual_market['marketHash'] + ' '
        # odds
        if 'outcomes' in self._actual_market['description']:

            n_outcomes = len(self._actual_market['description']['outcomes'])

            for x in range(0, n_outcomes):
                message += self._actual_market['description']['outcomes'][x]

                if x != n_outcomes-1:
                    message += '/'

        res = api.update_status(message)

        # Set memcache
        self.add_to_memcache('market_hash', self._actual_market_hash)
