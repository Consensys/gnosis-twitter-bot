import os
import environ

MEMCACHED_URL = os.getenv('MEMCACHED_URL', '127.0.0.1:11211')
GNOSIS_TWITTER_NAME = '@gnosismarketbot'
GNOSIS_URL = 'https://uport.gnosis.pm/#/market/'
UPORT_URL = 'https://www.uport.me/'
#MARKET_MANAGER_DIR = '../market-manager/'
#GET_MARKETS_FILE = 'getMarkets.js'
#GET_QR_FILE = 'getQR.js'

ROOT_DIR = environ.Path(__file__) - 3
GET_MARKETS_FILE = str(ROOT_DIR.path('market-manager/getMarkets.js'))
GET_QR_FILE = str(ROOT_DIR.path('market-manager/getQR.js'))

MEMCACHED_LOCKING_TIME= (5*60) # 5 mins in seconds
TWITTER_SCREEN_NAME='gnosismarketbot'
