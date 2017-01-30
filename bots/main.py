from publisher_bot.publisher_bot import PublisherBot
from botFactory import BotFactory
import memcache

if __name__=='__main__':

    memcache = memcache.Client([PublisherBot.MEMCACHE_URL], cache_cas=True)
    bot = BotFactory()
    bot.authenticate()

    if memcache.get('bot_started'):
        # the program is already running
        bot.start_publisher_bot()
        print "bot already started, publish new markets"
    else:
        print "Getting ready... new bot started"
        bot.start_trader_bot()
        memcache.set('bot_started', True)
