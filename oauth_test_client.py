from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for
from flask.json import jsonify
import os

app = Flask(__name__)


client_id = "wyULKchGsMW7r5ZSNaMSnSseDSmUthrQvrUqx4Oa"
client_secret = "t5FRJxpm7vtvn3W3j7wWRMgtqTmRSFKG1sC8C7L5QsoWX20amr4R5phd1ooT7oqp5bAJRsEicFD450GsLLN1NZ9SDNYqCq1tDADZmBMqIm8Fmx86KgWjzrSW2D7ZiESr"

authorization_base_url = 'http://localhost:8000/api/v1/tenant/3efed4d9-f2ee-455e-b868-6f60ea8fdff6/oauth/authorize/'
token_url = 'http://localhost:8000/api/v1/tenant/3efed4d9-f2ee-455e-b868-6f60ea8fdff6/oauth/token/'


@app.route("/")
def demo():
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider (i.e. Github)
    using an URL with a few key OAuth parameters.
    """
    github = OAuth2Session(client_id)
    authorization_url, state = github.authorization_url(authorization_base_url)

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)


# Step 2: User authorization, this happens on the provider.

@app.route("/callback", methods=["GET"])
def callback():
    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """
    github = OAuth2Session(client_id, state=session['oauth_state'])
    print('>>>>', token_url, client_secret, request.url, session['oauth_state'])
    token = github.fetch_token(token_url, client_secret=client_secret,
                               authorization_response=request.url)

    # At this point you can fetch protected resources but lets save
    # the token and show how this is done from a persisted token
    # in /profile.
    session['oauth_token'] = token
    print(f'i got token: {token}')

    return redirect(url_for('.profile'))


@app.route("/profile", methods=["GET"])
def profile():
    """Fetching a protected resource using an OAuth 2 token.
    """
    github = OAuth2Session(client_id, token=session['oauth_token'])
    return jsonify(github.get('https://api.github.com/user').json())


if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

    app.secret_key = os.urandom(24)
    app.debug = True
    app.run()