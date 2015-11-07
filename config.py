import os


# This is bad... But I don't have the time
# to find the alternative
HOST_URL = ''

API_KEY = os.getenv('API_KEY', '')
API_SECRET = os.getenv('API_SECRET', '')

PROVIDER = 'Twitter'
PROVIDER_BASE_URL = 'https://api.twitter.com/'
PROVIDER_API_VERSION = '1.1'

REQUEST_TOKEN_EP = 'oauth/request_token'
OAUTH_LOGIN_EP = 'oauth/authenticate'
ACCESS_TOKEN_EP = 'oauth/access_token'

OAUTH_CALLBACK_URL = 'callback'
TWEET_FETCH_ENDPOINT = 'statuses/user_timeline.json'


AUTHORIZE_REDIRECT_URL = None

OAUTH_VERIFIER = None

ACCESS_TOKEN_SECRET = None
ACCESS_TOKEN = None

REQUEST_OAUTH_TOKEN = None
REQUEST_OAUTH_SECRET = None
REQUEST_TOKEN_ACQUIRED = False

IS_AUTHENTICATED = False
LOGGED_IN_MESSAGE = 'View your tweets'
