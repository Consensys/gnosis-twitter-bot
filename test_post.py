import twitter
from secrets import *
import time
from datetime import datetime

endpoint = 'https://api.twitter.com/1.1/statuses/update.json'


api = twitter.Api(consumer_key=consumer_key,
                  consumer_secret=consumer_secret,
                  access_token_key=access_token,
                  access_token_secret=access_token_secret)

for x in range(0, 5):
    now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    message = 'Hi Giacomo, message created via API (%s)' % now
    res = api.CheckRateLimit(endpoint)
    message += ' | Limit : %s , Remaining : %s ' % (res.limit, res.remaining)
    status = api.PostUpdate(message);
    #print status
    time.sleep(2)
