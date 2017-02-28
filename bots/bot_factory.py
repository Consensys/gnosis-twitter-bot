from auth_factory import AuthFactory
from publisher_bot.publisher_bot import PublisherBot
from trader_bot.trader_bot import TraderBot

class BotFactory:
    """Bot factory"""

    def __init__(self):
        self._auth = None
        self._publisher = None
        self._trader = None

    def authenticate(self):
        self._auth = AuthFactory()

    def start_publisher_bot(self):
        self._publisher = PublisherBot(self._auth)
        self._publisher.load_markets()
        self._publisher.tweet_new_market()

    def publish_newest_markets(self):
        self._publisher = PublisherBot(self._auth)        
        self._publisher.tweet_newest_markets()

    def start_trader_bot(self):
        self._trader = TraderBot(self._auth)
        self._trader.start_streaming()
