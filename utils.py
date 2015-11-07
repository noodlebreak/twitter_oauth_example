from urllib.parse import quote, quote_plus
from urllib.parse import parse_qs
from hashlib import sha1
from os.path import join
# from pprint import pprint
import hmac
import base64
import random
import time
import requests

import config as cfg

# Join together a bunch of strings
# to create a proper API endpoint for a request
make_url = lambda *args: join(*args)


def generate_nonce(length=32):
    """
    Generate pseudorandom number.
    """
    return ''.join(random.choice('0123456789abcdef') for i in range(length))


def generate_auth_header():
    """
    Does what the name says.
    """

    # Generic Authorization header data that
    # can be used across many API requests
    return dict(oauth_consumer_key=cfg.API_KEY,
                oauth_nonce=generate_nonce(),
                oauth_signature_method="HMAC-SHA1",
                oauth_timestamp=int(time.time()),
                oauth_version=1.0)


def format_auth_header_data(header_dict):
    """
    Creates the nicely formatted 'Authorization'
    header data string.
    """
    auth_data = ''
    for key in sorted(header_dict):
        value = header_dict[key]
        if not auth_data:
            auth_data += 'OAuth {}="{}"'.format(key, quote(str(value)))
        else:
            auth_data += ', {}="{}"'.format(key, quote(str(value)))
    return auth_data


def calc_hmac_signature(method, url, param_string_data, key):
    """
    Calculates HMAC SHA1 digest, as needed by Twitter
    """
    param_string = ''
    # Generate param string
    for k in sorted(param_string_data):
        if param_string is '':
            param_string += "{}={}".format(quote(k),
                                           quote(str(param_string_data[k])))
        else:
            param_string += "&{}={}".format(quote(k),
                                            quote(str(param_string_data[k])))

    signature_base_string = '&'.join(
        [method, quote_plus(url), quote_plus(param_string)])

    hashed = hmac.new(key.encode(), signature_base_string.encode(), sha1)
    hmac_res = base64.encodebytes(hashed.digest()).decode().strip('\n')
    return hmac_res.rstrip('\n')


def get_request_token():
    """
    Fetch a request token from Twitter API.
    """
    auth_data = ''  # Will store Authorization header string
    RT_HEADER = generate_auth_header()
    RT_HEADER['oauth_callback'] = make_url(
        cfg.HOST_URL, cfg.OAUTH_CALLBACK_URL)

    url = make_url(cfg.PROVIDER_BASE_URL, cfg.REQUEST_TOKEN_EP)
    signature = calc_hmac_signature(
        method='POST',
        url=url,
        param_string_data=RT_HEADER,
        key=cfg.API_SECRET + '&')

    RT_HEADER['oauth_signature'] = signature

    auth_data = format_auth_header_data(RT_HEADER)

    resp = requests.post(
        url,
        headers={'Authorization': auth_data})

    # print(resp.status_code)
    # print(resp.text)

    if resp.ok and resp.status_code is 200:
        parsed = parse_qs(resp.text)
        if parsed['oauth_callback_confirmed']:
            print("***** Request token acquired successfully *****\n")
            return (parsed['oauth_token_secret'][0], parsed['oauth_token'][0])


def get_oauth_access_token():
    """
    Method to exchange request token to get
    OAuth access token, which will enable us
    to make API requests on behalf of the
    logged in user.
    """
    # add oauth_token and oauth_signature to headers
    auth_header_data = generate_auth_header()
    body = dict(oauth_verifier=cfg.OAUTH_VERIFIER)
    url = make_url(cfg.PROVIDER_BASE_URL, cfg.ACCESS_TOKEN_EP)

    auth_header_data['oauth_token'] = cfg.REQUEST_OAUTH_TOKEN

    param_string_data = auth_header_data.copy()
    param_string_data['oauth_verifier'] = cfg.OAUTH_VERIFIER

    hmac_key = '%s&%s' % (cfg.API_SECRET, cfg.REQUEST_OAUTH_SECRET)
    auth_header_data['oauth_signature'] = calc_hmac_signature(
        method='POST',
        url=url,
        param_string_data=param_string_data,
        key=hmac_key)

    auth_header_data = format_auth_header_data(auth_header_data)

    # send request, get oauth_token, oauth_token_secret
    resp = requests.post(
        url,
        headers={'Authorization': auth_header_data},
        data=body)

    if resp.status_code == 200:
        parsed_resp = parse_qs(resp.text)
        cfg.ACCESS_TOKEN = parsed_resp['oauth_token'][0]
        cfg.ACCESS_TOKEN_SECRET = parsed_resp['oauth_token_secret'][0]
        cfg.USER_ID = parsed_resp['user_id'][0]
        cfg.SCREEN_NAME = parsed_resp['screen_name'][0]

    else:
        print("\n---------- get_oauth_access_token FAILED -----------\n")
        print(resp.text, resp.status_code)


def extract_tweet(tweet):
    return tweet['text'], tweet['created_at']


def get_users_tweets(full=False):
    """
    Given a user details object,
    fetch tweets of that user.

    :full: If True, returns full json returned from Twitter.
           Else, only the tweet text and created_at
    """

    url = make_url(cfg.PROVIDER_BASE_URL,
                   cfg.PROVIDER_API_VERSION,
                   cfg.TWEET_FETCH_ENDPOINT)

    # add oauth_token and oauth_signature to headers
    auth_header_data = generate_auth_header()
    auth_header_data['oauth_token'] = cfg.ACCESS_TOKEN
    params = dict(screen_name=cfg.SCREEN_NAME, count=10)

    hmac_key = '%s&%s' % (cfg.API_SECRET, cfg.ACCESS_TOKEN_SECRET)

    param_string_data = auth_header_data.copy()
    param_string_data.update(params)
    auth_header_data['oauth_signature'] = calc_hmac_signature(
        method='GET',
        url=url,
        param_string_data=param_string_data,
        key=hmac_key)

    auth_header_string = format_auth_header_data(auth_header_data)

    # Tweet fetching
    tweets = requests.get(url,
                          headers={'Authorization': auth_header_string},
                          params=params)
    if not tweets.ok:
        return tweets.text

    if not full:
        tweets = [extract_tweet(tweet) for tweet in tweets.json()]

    return tweets
