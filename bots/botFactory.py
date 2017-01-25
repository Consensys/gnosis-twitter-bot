from authFactory import AuthFactory
from publisher_bot.publisher_bot import PublisherBot

class BotFactory:
    """Bot factory"""

    def __init__(self):
        self._auth = None
        self._publisher = None

    def authenticate(self):
        self._auth = AuthFactory()

    def start_publisher_bot(self):
        self._publisher = PublisherBot(self._auth)
        self._publisher.load_markets()
        self._publisher.tweet_new_market()


if __name__=='__main__':
    bot = BotFactory()
    bot.authenticate()
    bot.start_publisher_bot()
