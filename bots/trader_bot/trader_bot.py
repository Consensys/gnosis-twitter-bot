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
    LOG_DIR = 'logs/trader.log'

    def __init__(self, auth):
        self._auth = auth
        self._stream = None
        self._logger = None
        # setting up the logger
        self.setup_logger()
        self._logger.info("__init__")


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
        handler = logging.FileHandler(TraderBot.LOG_DIR)
        handler.setLevel(logging.INFO)
        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        # add the handlers to the logger
        self._logger.addHandler(handler)


    def on_error(self, status_code):
        self._logger.error(status_code)
        if status_code == 420:
            # returning False disconnects the stream
            return False


    def get_trading_and_token_number_from_string(self, tweet_text):
        """
        Returns an array containing the trading_type (1, -1) in 1st position
        and the number of tokens in 2nd position.
        Returns [False, False] if the input text doesn't contain the trading type ('Higher', 'Lower')
        """
        use_default_number_tokens = False
        number_of_tokens = None
        default_number_of_tokens = str(1)
        trading_type = None
        upper_text = tweet_text.upper()

        # Detect trading type
        # Check if text contains HIGHER or LOWER keyword
        upperText = upper_text.replace('@GNOSISMARKETBOT', '')
        if 'HIGHER' in upperText:
            trading_type = TraderBot.HIGHER_TRADE
            upperText = upperText.replace('HIGHER', '').strip()
        elif 'LOWER' in upperText:
            trading_type = TraderBot.LOWER_TRADE
            upperText = upperText.replace('LOWER', '').strip()
        else:
            # No valid input keyword found
            return [False, False]

        # Decode the amount of tokens invested
        # If the user doesn't provide the ETH amount
        # we consider it to be 1 ETH by default
        if trading_type == TraderBot.HIGHER_TRADE:
            upper_text = upper_text.replace('HIGHER', '').strip()
            if len(upper_text) == 0:
                use_default_number_tokens = True
        else:
            upper_text = upper_text.replace('LOWER', '').strip()
            if len(upper_text) == 0:
                use_default_number_tokens = True

        if not use_default_number_tokens:
            if 'ETH' in upper_text:
                number_of_tokens = ''.join(upper_text.replace('ETH', '').strip().split(' '))
            else:
                # Detect numbers
                _numbers = [char for char in upper_text.split(' ') if char.isdigit()]

                if len(_numbers) > 1:
                    # Adopt the default number of token value in
                    # case the user provided not valid words
                    number_of_tokens = default_number_of_tokens
                elif len(_numbers) == 1:
                    number_of_tokens = str(_numbers[0])
                else:
                    number_of_tokens = default_number_of_tokens
                    #''.join(upper_text.split(' '))
        else:
            number_of_tokens = default_number_of_tokens

        return [trading_type, number_of_tokens]


    def on_data(self, data):
        """This method is called when new tweets or replies are sent to the twitter account"""

        self._logger.info('Data received')
        json_data = json.loads(data)

        if 'text' in json_data and 'in_reply_to_screen_name' in json_data \
            and json_data['in_reply_to_screen_name'] == 'gnosismarketbot':

            tweet_text = json_data['text'] # get tweet text
            trading_type = None
            number_of_tokens = 1
            default_number_of_tokens = str(1)
            use_default_number_tokens = False
            tweet_id = json_data['id_str']
            tweet_reply_id = json_data['in_reply_to_status_id']
            received_from = json_data['user']['screen_name']
            response = self._auth.get_api().get_status(tweet_reply_id)

            trading_type, number_of_tokens = self.get_trading_and_token_number_from_string(tweet_text)

            if not number_of_tokens:
                # re-tweet
                raise Exception('Invalid command provided')

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
                qr_data = None
                response_tweet_text = '@%s ' % received_from # Thanks for using TwitterBot with https://www.uport.me/\n' % received_from
                price_before_buying = 0
                price_after_buying = 0
                # Find the tweet related market
                n_markets = len(markets)
                for x in range(0, n_markets):
                    if markets[x]['marketHash'] == market_hash:
                        market = markets[x]
                        break

                if market:
                    # determine if it is ranged or discrete
                    if 'outcomes' in market['description']:
                        # Discrete event
                        if trading_type == TraderBot.HIGHER_TRADE:
                            # call qr - outcomeIndex = 0
                            qr_data = self.get_qr_data(market_hash, market_address, 0, number_of_tokens)
                        else:
                            # call qr - outcomeIndex = 1
                            qr_data = self.get_qr_data(market_hash, market_address, 1, number_of_tokens)

                        price_before_buying = str(float(qr_data['priceBeforeBuying'])*100)
                        price_after_buying = str(float(qr_data['priceAfterBuying'])*100)

                        response_tweet_text += 'By sending %s ETH the prediction will change from Yes %s%% to Yes %s%%.' % (str(number_of_tokens), price_before_buying, price_after_buying)
                    else:
                        # Ranged event
                        if trading_type == TraderBot.HIGHER_TRADE:
                            # call qr - outcomeIndex = 1
                            qr_data = self.get_qr_data(market_hash, market_address, 1, number_of_tokens)
                        else:
                            # call qr - outcomeIndex = 0
                            qr_data = self.get_qr_data(market_hash, market_address, 0, number_of_tokens)

                        price_before_buying = str(qr_data['priceBeforeBuying'])
                        price_after_buying = str(qr_data['priceAfterBuying'])
                        response_tweet_text += 'By sending %s ETH the prediction will change from %s USD to %s USD' % (str(number_of_tokens), price_before_buying, price_after_buying)

                    # encode Qr and reply to the received tweet
                    self._logger.info('Calling self.retweet')
                    #response_tweet_text = '@%s Thanks for using TwitterBot with https://www.uport.me/\nShares to buy %s\nPrice after buying %s' % (received_from, str(qr_data['numberOfShares']), str(qr_data['priceAfterBuying']))
                    self.retweet(response_tweet_text, tweet_id, qr_data['imageString'])

            except:
                self._logger.error('Exception thrown: %s', exc_info=True)


    def get_qr_data(self, market_hash, market_address, outcome_index, number_of_tokens):
        """Calls a nodejs script which returns the qrcode content to decode"""

        qr_string = None
        try:
            # Call node script getQR.js
            process = Popen(["node", PublisherBot.MARKET_MANAGER_DIR + PublisherBot.GET_QR_FILE, market_hash, str(outcome_index), market_address, str(number_of_tokens)], stdout=PIPE)
            (output, err) = process.communicate()
            exit_code = process.wait()

            if err:
                raise Exception(err)

            #self._logger.info(output);
            qr_data = json.loads(output)
            return qr_data

        except:
            self._logger.error('An error occurred in get_qr_data', exc_info=True)


    def retweet(self, tweet_text, tweet_id, qr_image_string):
        """Send a tweet in reply to the receiving message, attaching the generated qrcode"""

        # TODO
        # Tweepy API.update_with_media seems to work only by providing
        # a file placed on filesystem. Files creation/deletion should be managed.
        self._logger.info('Creating qrcode')
        # Create qrcode image
        try:
            with open("qrcodes/qr_code.png", "wb") as fh:
                fh.write(qr_image_string.decode('base64'))

            self._logger.info('saving qrcode to file')

            # TODO create an unique image name
            # and remove it after sendig back the tweet
            self._logger.info('qrcode saved')
            self._logger.info('Retweeting')
            # Retweet
            try:
                #self._logger.info(tweet_text)
                response = self._auth.get_api().update_with_media('qrcodes/qr_code.png', status=tweet_text, in_reply_to_status_id=tweet_id)
                self._logger.info('Tweet sent')
                #self._logger.info(response)
            except:
                self._logger.error('An error occurred in retweet when sending response back via API', exc_info=True)

        except:
            self._logger.error('An error occurred in retweet:', exc_info=True)


    def start_streaming(self):
        """Starts listening to the streaming API"""
        self._logger.info('Starting streaming...')
        self._stream = tweepy.Stream(auth=self._auth.get_authentication(), listener=self._instance)
        self._stream.userstream(replies=True, async=True)
        self._logger.info('Streaming started')
