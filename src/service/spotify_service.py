import logging
import requests
import urllib.parse
from requests import Request
from util import song_util

from service import secrets_service, session_service, authorization_service
from constants import SPOTIFY_CLIENT_ID

LOGGER = logging.getLogger(__name__)

REDIRECT_URI = 'http://localhost:3000/callback'
SEARCH_URL = 'https://api.spotify.com/v1/search?'
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
        'client_secret': secrets_service.get_spotify_secret_key()
    }


def first_time_spotify_authorization(code, username):
    params = create_token_request_body(code)
    response = requests.post(TOKEN_URL, data=params)

    LOGGER.info(f'response:\n{response}')
    if response.status_code != 200:
        raise Exception(f'Received response with status code {response.status_code} from Spotify auth endpoint')

    json = response.json()
    access_token = json.get('access_token')
    refresh_token = json.get('refresh_token')

    authorization_service.save_access_token(username, access_token)
    authorization_service.save_refresh_token(username, refresh_token)

    LOGGER.info(f'access_token: {access_token}\nrefresh_token: {refresh_token}')

#
# Searches Spotify for the closest match to the provide tracks
#
def get_spotify_tracks(track_dictionary_list, access_token):
    spotify_tracks = []
    for track_dictionary in track_dictionary_list:
        spotify_track = search_for_song(track_dictionary['artist'], track_dictionary['title'], access_token)
        if spotify_track is not None:
            spotify_tracks.append(spotify_track)

    LOGGER.info(f'\n\nSpotify tracks post-formatting: {spotify_tracks}')


def search_for_song(artist, song_title, access_token):
    LOGGER.info(f'\n\nSearching for track {artist} - {song_title}')

    payload = {'q': f'artist:{artist} title:{song_title}', 'type': 'track', 'limit': '3'}
    params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)
    search_response = requests.get(SEARCH_URL + params, headers={'Authorization': f'Bearer {access_token}'})

    if (search_response.status_code != 200):
        LOGGER.error(f'Received {search_response.status_code} response from Spotify search')
        return None

    return get_spotify_track_attributes(search_response.json())


def get_spotify_track_attributes(spotify_response):
    try:
        artist = spotify_response['tracks']['items'][0]['artists'][0]['name']
        title = spotify_response['tracks']['items'][0]['name']
        return song_util.create_artist_song_dict(artist, title)
    except:
        LOGGER.error(f'Error grabbing Spotify song attributes')
        return None
