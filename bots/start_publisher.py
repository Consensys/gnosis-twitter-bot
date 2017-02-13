from publisher_bot.publisher_bot import PublisherBot
from bot_factory import BotFactory
import memcache

if __name__=='__main__':
    memcache = memcache.Client([PublisherBot.MEMCACHE_URL], cache_cas=True)
    bot = BotFactory()
    bot.authenticate()
    bot.start_publisher_bot()
