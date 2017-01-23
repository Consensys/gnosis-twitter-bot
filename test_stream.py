import tweepy
from secrets import *


class MyStreamListener(tweepy.StreamListener):
    
    def on_status(self, status):
        print(status.text)

    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_data disconnects the stream
            return False


    def on_data(self, data):
        print "data received"
        print data




auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = auth, listener=myStreamListener)
myStream.filter(track=['gnosismarketbot'], async=True)

