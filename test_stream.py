import tweepy
import json
from secrets import *


class GnosisStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        print status.text

    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_data disconnects the stream
            return False


    def on_data(self, data):
        print "on_data received"
        jsonData = json.loads(data)
        #"text":"@gnosismarketbot Hello2"
        #"in_reply_to_screen_name":"gnosismarketbot",
        print data

    def on_direct_message(self, data):
        print "on_direct received"
        print data




auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

gnosisListener = GnosisStreamListener()
stream = tweepy.Stream(auth = auth, listener=gnosisListener)

#def userstream(self, stall_warnings=False, _with=None, replies=None,
#track=None, locations=None, async=False, encoding='utf8'):
stream.userstream(replies=True, async=True)
#def filter(self, follow=None, track=None, async=False, locations=None,
#stall_warnings=False, languages=None, encoding='utf8', filter_level=None):
#stream.filter(track=[''], async=True)

#import inspect
#methods = inspect.getmembers(tweepy.StreamListener, predicate=inspect.ismethod)
#print methods
