from publisher_bot.publisher_bot import PublisherBot
from subprocess import Popen, PIPE
from StringIO import StringIO
import base64
import qrcode
import tweepy
import json
import logging
import sys

class TraderBot(tweepy.StreamListener, object):
    """Trader bot class"""

    _instance = None

    HIGHER_TRADE = 1
    LOWER_TRADE = -1

    def __init__(self, auth):
        self._auth = auth
        self._stream = None
        self.setup_logger()


    def __new__(self, auth):
        if auth:
            if not TraderBot._instance:
                TraderBot._instance = super(TraderBot, self).__new__(self, auth)

            return TraderBot._instance
        else:
            raise Exception('Authentication not provided')


    def setup_logger(self):
        """Sets up the logger file"""

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)
        # create a file handler
        handler = logging.FileHandler('trader.log')
        handler.setLevel(logging.INFO)
        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        # add the handlers to the logger
        self._logger.addHandler(handler)


    # def on_status(self, status):
    #     print status.text


    def on_error(self, status_code):
        self._logger.error(status_code)
        if status_code == 420:
            # returning False disconnects the stream
            return False


    def on_data(self, data):
        """This method is called when new tweets or replies are sent to the twitter account"""

        self._logger.info('Data received')
        json_data = json.loads(data)

        if 'text' in json_data and 'in_reply_to_screen_name' in json_data \
            and json_data['in_reply_to_screen_name'] == 'gnosismarketbot':

            tweet_text = json_data['text'] # get tweet text
            trading_type = None
            tweet_id = json_data['id_str']
            tweet_reply_id = json_data['in_reply_to_status_id']
            received_from = json_data['user']['screen_name']
            response = self._auth.get_api().get_status(tweet_reply_id)

            # Check if text contains HIGHER or LOWER keyword
            if 'HIGHER' in tweet_text.upper():
                trading_type = TraderBot.HIGHER_TRADE
            elif 'LOWER' in tweet_text.upper():
                trading_type = TraderBot.LOWER_TRADE
            else:
                # No valid input keyword found
                return

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

                if market:
                    # determine if it is ranged or discrete
                    if 'outcomes' in market['description']:
                        if trading_type == TraderBot.HIGHER_TRADE:
                            # call qr - outcomeIndex = 0
                            qr_string = self.get_qr_text(market_hash, market_address, 0)
                        else:
                            # call qr - outcomeIndex = 1
                            qr_string = self.get_qr_text(market_hash, market_address, 1)
                    else:
                        if trading_type == TraderBot.HIGHER_TRADE:
                            # call qr - outcomeIndex = 1
                            qr_string = self.get_qr_text(market_hash, market_address, 1)
                        else:
                            # call qr - outcomeIndex = 0
                            qr_string = self.get_qr_text(market_hash, market_address, 0)
            except:
                self._logger.error('Exception thrown: %s', [sys.exc_info()[0]])

            # encode Qr and reply to the received tweet
            self._logger.info('Calling self.retweet')
            self.retweet('@%s Thanks for using TwitterBot' % received_from, tweet_id, qr_string)


    # def on_direct_message(self, data):
    #     print "on_direct received"
    #     print data


    def get_qr_text(self, market_hash, market_address, outcome_index):
        """Calls a nodejs script which returns the qrcode content to decode"""

        qr_string = None
        try:
            # Call node script getQR.js
            process = Popen(["node", PublisherBot.MARKET_MANAGER_DIR + PublisherBot.GET_QR_FILE, market_hash, str(outcome_index), market_address], stdout=PIPE)
            (output, err) = process.communicate()
            exit_code = process.wait()

            qr_string = output

            if err:
                #TODO define what to do with returning errors
                pass

            return qr_string

        except:
            self._logger.error('An error occurred in get_qr_text: %s', [sys.exc_info()[0]])
            raise


    def retweet(self, notification, tweet_id, qr_text):
        """Send a tweet in reply to the receiving message, attaching the generated qrcode"""

        # TODO
        # Tweepy API.update_with_media seems to work only by providing
        # a file placed on filesystem. Files creation/deletion should be managed.
        self._logger.info('Creating qrcode')
        # Create qrcode image
        qr_image = qrcode.make(qr_text)
        #img_buffer = StringIO()
        #qr_image.save(img_buffer)
        qr_image.save("qrcodes/qr_code.png")
        self._logger.info('qrcode saved')
        #raw_qr_code = img_buffer.getvalue()
        #qr_image_base64 = base64.b64encode(raw_qr_code)

        self._logger.info('Retweeting')
        # Retweet
        response = self._auth.get_api().update_with_media('qrcodes/qr_code.png', status=notification, in_reply_to_status_id=tweet_id)
        self._logger.info('Tweet sent')


    def start_streaming(self):
        """Starts listening to the streaming API"""
        self._logger.info('Starting streaming...')
        self._stream = tweepy.Stream(auth=self._auth.get_authentication(), listener=self._instance)
        self._stream.userstream(replies=True, async=True)
        self._logger.info('Streaming started')
