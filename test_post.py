import tweepy
from secrets import *
import time
from datetime import datetime

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

for x in range(0, 5):
    now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    message = 'Hi Giacomo, message created via API with Tweepy (%s)' % now
    api.update_status(message)
    
    time.sleep(2)
