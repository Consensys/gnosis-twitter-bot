import os
import environ

MEMCACHED_URL = os.getenv('MEMCACHED_URL', '127.0.0.1:11211')
GNOSIS_TWITTER_NAME = os.getenv('GNOSIS_TWITTER_NAME')
TWITTER_SCREEN_NAME= os.getenv('TWITTER_SCREEN_NAME')
GNOSIS_URL = 'https://uport.gnosis.pm/#/market/'
UPORT_URL = 'https://www.uport.me/'

ROOT_DIR = environ.Path(__file__) - 3
GET_MARKETS_FILE = str(ROOT_DIR.path('market-manager/getMarkets.js'))
GET_QR_FILE = str(ROOT_DIR.path('market-manager/getQR.js'))

USER_LOCKING_TIME= (5*60) # 5 mins in seconds

MONGODB_HOST = os.getenv('MONGODB_HOST', 'localhost')
MONGODB_PORT = os.getenv('MONGODB_PORT', 27017)
MONGODB_USERNAME = os.getenv('MONGODB_USERNAME', 'twitterbot')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'twitterbot')
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD', 'root')