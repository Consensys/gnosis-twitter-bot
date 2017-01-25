from subprocess import Popen, PIPE
import memcache
import json
import tweepy
#import time
from datetime import datetime

class PublisherBot(object):
    """Publisher bot class"""

    _instance = None

    def __init__(self, auth):
        self._auth = auth
        self._actual_market = {}
        self._markets = []
        self._memcache = memcache.Client(['127.0.0.1:11211'], cache_cas=True)

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

        # 1st chech if cache contains the actual hash
        if self._memcache.get('market_hash'):

            self._actual_market = self._memcache.get('market_hash')

            # Find the next market hash
            n_markets = len(self._markets)

            for x in range(0, n_markets):
                if self._markets[x]['marketHash'] == self._actual_market:
                    if x == n_markets-1:
                        self._actual_market = self._markets[0]['marketHash']
                    else:
                        self._actual_market = self._markets[x+1]['marketHash']

                self._memcache.set('market_hash', self._actual_market)
        else:
            # Set the first element of the markets array
            self._actual_market = self._markets[0]['marketHash']
            self._memcache.set('market_hash', self._actual_market)

    def tweet_new_market(self):
        api = self._auth.get_api()
        now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        message = 'Message created by GnosisMarketBot - (%s)' % now
        api.update_status(message)
