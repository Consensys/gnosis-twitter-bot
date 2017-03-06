from subprocess import Popen, PIPE
import os
import memcache
import json
import tweepy
import time
# from utils.memcached import Memcached as memcached
from utils.constants import GET_MARKETS_FILE, GNOSIS_URL
from utils.connection import MongoConnection
from datetime import datetime


class PublisherBot(object):
    """Publisher bot class"""

    _instance = None

    def __init__(self, auth):
        self._auth = auth
        self._actual_market = {}
        self._actual_market_hash = None
        self._markets = []

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
            process = Popen(["node", GET_MARKETS_FILE, "."], stdout=PIPE, stderr=PIPE)
            (output, err) = process.communicate()
            exit_code = process.wait()
            markets = json.loads(output)

            if err:
                pass #TODO define what to do with returning errors

            return markets

        except (ValueError, KeyError, TypeError):
            raise

    def get_actual_market(self):
        return self._actual_market

    def sort_markets_by_createdAt(self, a, b):
        """
        Comparator which sorts a list of markets by createdAt attribute DESC.
        CreatedAt must be compliant with ISO-8601, example: 2017-02-27T17:39:03.000Z
        """
        date_a = datetime.strptime(a['createdAt'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
        date_b = datetime.strptime(b['createdAt'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
        if a < b:
            return 1
        elif b < a:
            return -1
        else:
            return 0

    def tweet_newest_markets(self):
        """
        Publishes the newest markets.
        This method should be called repeatedly in order to publish
        the latest markets created.
        """
        n_markets = None
        n_new_markets = None

        try:
            self._markets = self.get_markets()
            n_markets = len(self._markets)

            if n_markets == 0:
                raise Exception('No markets found')

        except Exception:
            raise

        db_response = MongoConnection().get_database().markets.find_one()

        if db_response is not None and db_response['number_of_markets']: # Number of markets got previously
        # if memcached.get('number_of_markets'):
            # if memcached.get('number_of_markets') < n_markets:
            if db_response['number_of_markets'] < n_markets:
                n_new_markets = n_markets - db_response['number_of_markets'] # memcached.get('number_of_markets')

                # One or more events have been published
                sorted_markets = sorted(self._markets, cmp=self.sort_markets_by_createdAt)
                # Get new markets
                new_markets = sorted_markets[0:n_new_markets]

                for market in new_markets:
                    self._actual_market = market
                    self.tweet_new_market(False)
                    time.sleep(1)

            # Update memcached number_of_markets
            # memcached.add('number_of_markets', n_markets)
            MongoConnection().get_database().markets.update_one({'_id':db_response['_id']}, {'$set':{'number_of_markets':n_markets}})
        else:
            # Memcached variable wasn't setted
            # memcached.add('number_of_markets', len(self._markets))
            n_markets = len(self._markets)
            MongoConnection().get_database().markets.insert_one({'number_of_markets':n_markets, 'market_hash': self._markets[0]})

    def load_markets(self):
        """
        Loads new markets and stores the next market to publish
        """
        n_markets = None

        try:
            self._markets = self.get_markets()
            n_markets = len(self._markets)

            if n_markets == 0:
                raise Exception('No markets found')

        except Exception:
            raise

        # 1st chech if cache contains the market hash
        db_response = MongoConnection().get_database().markets.find_one()

        if db_response is not None and db_response['market_hash']:

            self._actual_market_hash = db_response['market_hash']

            # Find the next available market hash
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


    def tweet_new_market(self, set_market_hash=True):
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
        message += ' ' + GNOSIS_URL
        message += self._actual_market['descriptionHash'] + '/'
        message += self._actual_market['marketAddress'] + '/'
        message += self._actual_market['marketHash'] + '?t=' + str(int(time.time()*1000))

        res = api.update_status(message)        

        if set_market_hash:
            # Set memcache
            # memcached.add('market_hash', self._actual_market_hash)
            MongoConnection().get_database().markets.update_one({
                'market_hash':self._actual_market['marketHash']
                },
                {
                    '$set' : {
                        'number_of_markets':len(self._markets)
                    }
                },
                upsert=True
            )

