from publisher_bot.publisher_bot import PublisherBot
from subprocess import Popen, PIPE
import tweepy
import json
import sys

class TraderBot(tweepy.StreamListener, object):
    """Trader bot class"""

    _instance = None

    HIGHER_TRADE = 1
    LOWER_TRADE = -1

    def __init__(self, auth):
        self._auth = auth
        self._stream = None
        #self._memcache = memcache.Client([PublisherBot.MEMCACHE_URL], cache_cas=True)


    def __new__(self, auth):
        if auth:
            if not TraderBot._instance:
                TraderBot._instance = super(TraderBot, self).__new__(self, auth)

            return TraderBot._instance
        else:
            raise Exception('Authentication not provided')


    # def on_status(self, status):
    #     print status.text


    # def on_error(self, status_code):
    #     if status_code == 420:
    #         #returning False in on_data disconnects the stream
    #         return False


    def on_data(self, data):
        json_data = json.loads(data)

        if 'text' in json_data and 'in_reply_to_screen_name' in json_data and json_data['in_reply_to_screen_name'] == 'gnosismarketbot':
            tweet_text = json_data['text']
            trading_type = None
            response = self._auth.get_api().get_status(json_data['in_reply_to_status_id'])

            # Check if text contains HIGHER or LOWER keyword
            if 'HIGHER' in tweet_text.upper():
                trading_type = TraderBot.HIGHER_TRADE
            elif 'LOWER' in tweet_text.upper():
                trading_type = TraderBot.LOWER_TRADE
            else:
                # No valid input keyword found
                return

            # TODO check if json has data, error handling
            # Example URL
            # https://beta.gnosis.pm/#/market/
            # 0x6fd8230f876fbb8137de15f05c1065d3008c030daa970fd19ba1a7b412440636/
            # 0x9b40645cbc6142cdfd5441a9ad4afde8da8ed199/
            # 0xb914c6ecbd26da9b146499bac3c91b5236fbdae3ec1b2896323722943c022f39?t=1485430823089
            market_url = response._json['entities']['urls'][0]['expanded_url']
            url_components = market_url[len(PublisherBot.GNOSIS_URL)::].split('/')
            description_hash = url_components[0]
            market_address = url_components[1]
            market_hash = url_components[2].split('?')[0]

            # Parse json_data and get the outcome by calling PublisherBot
            publisher_bot = PublisherBot(self._auth)
            try:
                markets = publisher_bot.get_markets()
                market = None
                outcomeIndex = None
                qr_string = None
                # Find the tweet related market
                n_markets = len(markets)
                for x in range(0, n_markets):
                    if markets[x]['marketHash'] == market_hash:
                        market = markets[x]
                        break

                # TODO remove print commands
                print "Market address : " + market_address
                print "Market hash : " + market_hash
                print "Description hash : " + description_hash

                if market:
                    # determine if it is ranged or discrete
                    if 'outcomes' in market['description']:
                        if trading_type == TraderBot.HIGHER_TRADE:
                            # call qr - outcomeIndex = 0
                            qr_string = self.get_qr(market_hash, market_address, 0)
                        else:
                            # call qr - outcomeIndex = 1
                            qr_string = self.get_qr(market_hash, market_address, 1)
                    else:
                        if trading_type == TraderBot.HIGHER_TRADE:
                            # call qr - outcomeIndex = 1
                            qr_string = self.get_qr(market_hash, market_address, 1)
                        else:
                            # call qr - outcomeIndex = 0
                            qr_string = self.get_qr(market_hash, market_address, 0)
            except:
                pass

            # encode Qr

            # reply to the received tweet


    def on_direct_message(self, data):
        print "on_direct received"
        print data


    def get_qr(self, market_hash, market_address, outcome_index):
        qr_string = None
        try:
            # Call node script getQR.js
            process = Popen(["node", PublisherBot.MARKET_MANAGER_DIR + PublisherBot.GET_QR_FILE, market_hash, str(outcome_index), market_address], stdout=PIPE)
            (output, err) = process.communicate()
            exit_code = process.wait()

            qr_string = output

            if err:
                # pass #TODO define what to do with returning errors

            return qr_string

        except:
            #print sys.exc_info()
            raise


    def retweet(self, notification, tweet_id, qr_image):
        # API.update_with_media
        pass


    def start_streaming(self):
        self._stream = tweepy.Stream(auth=self._auth.get_authentication(), listener=self._instance)
        self._stream.userstream(replies=True, async=True)
