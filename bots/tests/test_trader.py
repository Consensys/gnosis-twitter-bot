import unittest
import environ
import json
import time
from subprocess import Popen, PIPE
from auth_factory import AuthFactory
from trader_bot.trader_bot import TraderBot
from publisher_bot.publisher_bot import PublisherBot
from utils.constants import GET_MARKETS_FILE, GET_QR_FILE, MEMCACHED_LOCKING_TIME
from utils.memcached import Memcached as memcached


class TestTrader(unittest.TestCase):
    """python -m unittest tests.test_trader"""

    def __init__(self, *args, **kwargs):
        super(TestTrader, self).__init__(*args, **kwargs)


    def setUp(self):
        self.auth = AuthFactory()
        self.trader = TraderBot(self.auth)
        self.publisher = PublisherBot(self.auth)

        # Mock trader methods
        def retweet(tweet_text, tweet_id):
            pass

        def retweet_with_media(tweet_text, tweet_id, qr_image_string):
            pass

        def get_reply_id_status(tweet_reply_id):
            class Response:
                def __init__(self):
                    self._json = json.loads(json.dumps({"entities" : {"urls" : [{"expanded_url":"https://beta.gnosis.pm/#/market/0x6fd8230f876fbb8137de15f05c1065d3008c030daa970fd19ba1a7b412440636/0x9b40645cbc6142cdfd5441a9ad4afde8da8ed199/0xb914c6ecbd26da9b146499bac3c91b5236fbdae3ec1b2896323722943c022f39?t=1485430823089"}]}}))

            return Response()

        def get_markets():
            markets = []
            process = Popen(["node", GET_MARKETS_FILE, "."], stdout=PIPE, stderr=PIPE)
            (output, err) = process.communicate()
            exit_code = process.wait()
            markets = json.loads(output)

            return markets


        self.trader.retweet = retweet
        self.trader.retweet_with_media = retweet_with_media
        self.trader.get_reply_id_status = get_reply_id_status
        self.publisher.get_markets = get_markets


    def test_bot_commands(self):

        commands = [
            ["higher 2eth", "2"],
            ["higher 2 eth", "2"],
            ["higher", "1"],
            ["higher hte", "1"],
            ["higher 1 hte", "1"],
            ["lower", "1"],
            ["lower 2", "2"],
            ["lower 2eth", "2"],
            ["lower", "1"],
            ["lower hte", "1"],
            ["lower 2hte", "1"],
            ["lower 1 hte", "1"],
            ["1 hte", False]
        ]

        [self.assertEquals(self.trader.get_trading_and_token_number_from_string(cmd[0].upper())[1], cmd[1]) for cmd in commands]


    def test_locking_system(self):
        timestamp = time.time() # in seconds
        test_user_id = "123456"
        memcached.delete(test_user_id)
        # Verify if userid in memcached
        last_tweet_timestamp = memcached.get(test_user_id)
        self.assertIsNone(last_tweet_timestamp)
        memcached.add(test_user_id, timestamp)

        last_tweet_timestamp = memcached.get(test_user_id)
        self.assertEquals(last_tweet_timestamp, timestamp)

        second_timestamp = time.time()
        self.assertTrue((timestamp - last_tweet_timestamp) <= MEMCACHED_LOCKING_TIME)  


    def test_node_errors(self):
        market_hash = "fake_market_hash"
        outcome_index = 1
        market_address = "0x9b40645cbc6142cdfd5441a9ad4afde8da8ed199"
        number_of_tokens = 1

        process = Popen(["node", GET_QR_FILE, market_hash, str(outcome_index), market_address, str(number_of_tokens)], stdout=PIPE)
        (output, err) = process.communicate()
        exit_code = process.wait()

        self.assertTrue(exit_code==1) # code 1 means the program terminated with errors


if __name__=='__main__':
    unittest.main()
