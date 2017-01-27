from botFactory import BotFactory

if __name__=='__main__':
    bot = BotFactory()
    bot.authenticate()
    bot.start_publisher_bot()
    bot.start_trader_bot()
