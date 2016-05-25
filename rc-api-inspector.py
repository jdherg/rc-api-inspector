import os

from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth

app = Flask(__name__)
PROXY_BASE = os.environ.get('PROXY_BASE', None)
app.secret_key = os.environ.get('SESSIONS_KEY', None)
oauth = OAuth(app)
rc = oauth.remote_app(
    'recurse_center',
    access_token_method='POST',
    access_token_url='https://www.recurse.com/oauth/token',
    authorize_url='https://www.recurse.com/oauth/authorize',
    base_url='https://www.recurse.com/api/v1/',
    consumer_key=os.environ.get('CONSUMER_KEY', None),
    consumer_secret=os.environ.get('CONSUMER_SECRET', None)
)


@app.route('/')
def index():
    if 'rc_token' in session:
        user = rc.get('people/me')
        return jsonify(user.data)
    return redirect(url_for('login'))


@app.route('/login')
def login():
    if PROXY_BASE is not None:
        return rc.authorize(callback=PROXY_BASE + url_for('authorized'))
    else:
        return rc.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('rc_token', None)
    return redirect(url_for('index'))


@app.route('/login/authorized')
def authorized():
    resp = rc.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error'],
            request.args['error_description']
        )
    session['rc_token'] = (resp['access_token'], resp['refresh_token'])
    return redirect(url_for('index'))


@rc.tokengetter
def get_recurse_center_oauth_token():
    return session.get('rc_token')

if __name__ == '__main__':
    app.run()
