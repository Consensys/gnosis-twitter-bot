from publisher_bot.publisher_bot import PublisherBot
from botFactory import BotFactory
import memcache

if __name__=='__main__':
    memcache = memcache.Client([PublisherBot.MEMCACHE_URL], cache_cas=True)
    bot = BotFactory()
    bot.authenticate()
    bot.start_trader_bot()