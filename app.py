import utils

from flask import Flask, request
from flask import render_template
from flask import redirect

import config as cfg

app = Flask(__name__)

p = print


@app.route('/')
def home():
    """
    If logged in, the user will be shown
    the link to view their latest tweets.

    Otherwise a link to authenticate them
    will be available.
    """

    if not cfg.HOST_URL:
        cfg.HOST_URL = request.base_url
        p('Host url set: %s' % cfg.HOST_URL)

    # Do not call Twitter again if already acquired
    if not cfg.REQUEST_TOKEN_ACQUIRED:
        p('cfg.REQUEST_TOKEN_ACQUIRED NOT SET\n')
        # Step 1 - Get request token
        reqtoken = utils.get_request_token()
        if reqtoken:
            cfg.REQUEST_TOKEN_ACQUIRED = True
            p('cfg.REQUEST_TOKEN_ACQUIRED SET = {}'.format(
                cfg.REQUEST_TOKEN_ACQUIRED))

            cfg.REQUEST_OAUTH_SECRET = reqtoken[0]
            cfg.REQUEST_OAUTH_TOKEN = reqtoken[1]
            cfg.AUTHORIZE_REDIRECT_URL = utils.make_url(
                cfg.PROVIDER_BASE_URL, cfg.OAUTH_LOGIN_EP,
                '?oauth_token=%s' % cfg.REQUEST_OAUTH_TOKEN)
            p('cfg.AUTHORIZE_REDIRECT_URL = %s' % cfg.AUTHORIZE_REDIRECT_URL)
    return render_template('home.html',
                           login_url=cfg.AUTHORIZE_REDIRECT_URL,
                           provider=cfg.PROVIDER,
                           success=cfg.REQUEST_TOKEN_ACQUIRED,
                           logged_in=cfg.IS_AUTHENTICATED,
                           logged_in_message=cfg.LOGGED_IN_MESSAGE)


@app.route('/callback')
def callback():
    """
    Our endpoint to parse and store the
    oauth_token and oauth_verifier received
    after the user authorizes our app
    """
    # headers = utils.generate_auth_header()
    cfg.OAUTH_TOKEN = request.args['oauth_token']
    cfg.OAUTH_VERIFIER = request.args['oauth_verifier']

    p("cfg.OAUTH_TOKEN:{} and cfg.OAUTH_VERIFIER:{}".format(
        cfg.OAUTH_TOKEN, cfg.OAUTH_VERIFIER))
    # Step 2 - User should click the login url,
    # and then we'll get the oauth_token and verifier
    # in a GET request to our callback here.

    # RT from step 1 must be equal to OT from step 2 (Twitter)
    if cfg.OAUTH_TOKEN == cfg.REQUEST_OAUTH_TOKEN:
        p("cfg.OAUTH_TOKEN == cfg.REQUEST_OAUTH_TOKEN")
        # Step 3 - exchange request token for access token
        utils.get_oauth_access_token()

        if cfg.ACCESS_TOKEN and cfg.ACCESS_TOKEN_SECRET:
            p("SUCCESS Acquired accesstoken:{} and accesstokensecret:{}".format(
                cfg.ACCESS_TOKEN, cfg.ACCESS_TOKEN_SECRET))
            # Finally, we have access tokens
            # to do API calls on behalf of the authenticated user
            cfg.IS_AUTHENTICATED = True
        else:
            p("FAILURE access token and secret not acquired")
            p("Acquired accesstoken:{} and accesstokensecret:{}".format(
                cfg.ACCESS_TOKEN, cfg.ACCESS_TOKEN_SECRET))
    else:
        p("cfg.OAUTH_TOKEN != cfg.REQUEST_OAUTH_TOKEN")

    cfg.AUTHENTICATION_TRIED = True
    return redirect('/')


@app.route('/view_data')
def view_data():
    """
    View which shows an authenticated user their
    data. Tweets, in case of Twitter.
    """
    tweets = 'Not authenticated'
    failure_message = None

    p("cfg.IS_AUTHENTICATED:{}, cfg.AUTHENTICATION_TRIED:{}".format(
        cfg.IS_AUTHENTICATED, cfg.AUTHENTICATION_TRIED))

    if cfg.IS_AUTHENTICATED:
        # Step 4 - Get user's tweets
        tweets = utils.get_users_tweets(full=False)

    if isinstance(tweets, str):
        failure_message = tweets
        tweets = None

    return render_template('tweets.html',
                           tweets=tweets,
                           failure_message=failure_message
                           )
if __name__ == '__main__':
    app.run(debug=True)
