from flask import Flask, redirect, request, render_template
import requests

app = Flask(__name__)

CLIENT_ID = 'client_id'
CLIENT_SECRET = 'client_secret'
REDIRECT_URI = 'http://localhost:5000/callback'

@app.route('/')
def home():
    auth_url = f'https://api.instagram.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=user_profile,user_media&response_type=code'
    return f'<a href="{auth_url}">Login with Instagram</a>'

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if code:
        access_token = get_access_token(code)
        if access_token:
            first_post = get_first_post(access_token)
            if first_post:
                return f'<img src="{first_post["media_url"]}" alt="First post">'
            else:
                return 'Error: Could not fetch the first post.'
        else:
            return 'Error: Could not obtain the access token.'
    else:
        return 'Error: Authorization failed.'

def get_access_token(code):
    token_url = 'https://api.instagram.com/oauth/access_token'
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
        'code': code
    }
    response = requests.post(token_url, data=payload)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        return None

def get_first_post(access_token):
    user_url = f'https://graph.instagram.com/me/media?fields=id,caption,media_type,media_url,thumbnail_url,timestamp&access_token={access_token}'
    response = requests.get(user_url)
    if response.status_code == 200:
        media = response.json()['data']
        sorted_media = sorted(media, key=lambda x: x['timestamp'])
        return sorted_media[0] if sorted_media else None
    else:
        return None

if __name__ == '__main__':
    app.run(debug=True)
