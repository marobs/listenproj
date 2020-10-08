import logging
import requests
import urllib.parse
from requests import Request

from dao import token_dao_in_memory
from service import secrets_service, session_service
from constants import SPOTIFY_CLIENT_ID

LOGGER = logging.getLogger(__name__)

REDIRECT_URI = 'http://localhost:3000/callback'
BASE_URL = 'https://accounts.spotify.com/authorize?'
SCOPES = [
    'user-library-modify',
    'user-library-read',
    'playlist-read-collaborative',
    'playlist-modify-private',
    'playlist-modify-public',
    'playlist-read-private'
]

TOKEN_URL = 'https://accounts.spotify.com/api/token'
TOKEN_GRANT_TYPE = 'authorization_code'

def create_oauth_params():
    return {
        'client_id':     SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'scope':         ' '.join(SCOPES),
        'redirect_uri':  REDIRECT_URI,
        'state':         session_service.get_state()
    }

def create_spotify_request_url():
    params = create_oauth_params()

    spotify_request_url = BASE_URL + urllib.parse.urlencode(params)
    LOGGER.info(f'request url:\n{spotify_request_url}')

    return spotify_request_url

def create_token_request_body(code):
    return {
        'grant_type': TOKEN_GRANT_TYPE,
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': secrets_service.get_secret_key()
    }

def first_time_spotify_authorization(code, username):
    params = create_token_request_body(code)
    response = requests.post(TOKEN_URL, data=params)

    LOGGER.info(f'response:\n{response}')
    if response.status_code != 200:
        raise Exception('Got bad response')

    json = response.json()
    access_token = json.get('access_token')
    refresh_token = json.get('refresh_token')

    token_dao_in_memory.save_access_token(username, access_token)
    token_dao_in_memory.save_refresh_token(username, refresh_token)

    LOGGER.info(f'access_token: {access_token}\nrefresh_token: {refresh_token}')

def create_playlist(song_list):
    for song in song_list:
        LOGGER.info(song)
    pass # TODO this 🍑🍆🍵☕


def search_for_song(song_title, access_token):
    URL = 'https://api.spotify.com/v1/search'
    params = {'q': song_title, 'type': 'track'}

    requests.get(URL, header={'auth': access_token}, params=urllib.parse.urlencode(params))
