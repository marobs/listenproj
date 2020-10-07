import logging
import requests
import urllib.parse
from requests import Request

import service.session_service as session_service
from constants import SPOTIFY_CLIENT_ID

LOGGER = logging.getLogger(__name__)

BASE_URL = 'https://accounts.spotify.com/authorize?'
SCOPES = [
    'user-library-modify',
    'user-library-read',
    'playlist-read-collaborative',
    'playlist-modify-private',
    'playlist-modify-public',
    'playlist-read-private'
]

def generate_oauth_params():
    return {
        'client_id':     SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'scope':         ' '.join(SCOPES),
        'redirect_uri':  "http://localhost:3000/",
        'state':         session_service.get_state()
    }

def generate_spotify_request_url():
    params = generate_oauth_params()

    spotify_request_url = BASE_URL + urllib.parse.urlencode(params)
    LOGGER.info(spotify_request_url)

    return spotify_request_url
