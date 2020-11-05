import logging
import requests
import urllib.parse
from requests import Request
from util import song_util
from dao import spotify_user_dao_in_memory as spotify_dao

from service import secrets_service, session_service, authorization_service
from constants import SPOTIFY_CLIENT_ID

LOGGER = logging.getLogger(__name__)

REDIRECT_URI = 'http://localhost:3000/callback'
GET_USER_URL = 'https://api.spotify.com/v1/me'
SEARCH_URL = 'https://api.spotify.com/v1/search?'
PLAYLIST_CREATE_URL_BASE = 'https://api.spotify.com/v1/users/{}/playlists'
PLAYLIST_ADD_URL_BASE = 'https://api.spotify.com/v1/playlists/{}/tracks'
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

def clear_spotify_dao():
    spotify_dao.clear()

def has_spotify_id(username):
    spotify_id = spotify_dao.get_user(username)
    return not not spotify_id

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

    LOGGER.info(f'\n\nSpotify tracks post-formatting:\n\n{spotify_tracks}\n\n')
    return spotify_tracks


def search_for_song(artist, song_title, access_token):
    LOGGER.info(f'\n\nSearching for track {artist} - {song_title}')

    payload = {'q': f'artist:{artist} track:\"{song_title}\"', 'type': 'track', 'limit': '3'}
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
        track_id = spotify_response['tracks']['items'][0]['id']
        uri = spotify_response['tracks']['items'][0]['uri']
        return song_util.create_track_dict(artist, title, track_id, uri)
    except:
        LOGGER.exception(f'Error grabbing Spotify song attributes')
        return None

#
# Gets the user's Spotify ID based on their access token
#
def get_spotify_id(username, access_token):
    spotify_id = spotify_dao.get_user(username)
    if spotify_id is not None:
        return spotify_id

    user_response_raw = requests.get(GET_USER_URL, headers={'Authorization': f'Bearer {access_token}'})
    user_response = user_response_raw.json()

    try:
        spotify_id = user_response['id']
        spotify_dao.save_spotify_id(username, spotify_id)
        return spotify_id
    except Exception as ex:
        LOGGER.exception(f'Error grabbing Spotify Id for user {username}')
        raise ex


#
# Creates a playlist with the specified tracks
#
def create_playlist_with_tracks(username, access_token, spotify_tracks):
    spotify_user_id = get_spotify_id(username, access_token)
    playlist_id = create_playlist(access_token, spotify_user_id)

    if playlist_id is None:
        return

    add_songs_to_playlist(access_token, playlist_id, spotify_tracks)

def create_playlist(access_token, spotify_user_id):
    create_playlist_url = PLAYLIST_CREATE_URL_BASE.format(spotify_user_id)
    request_body = {
        'name': 'Your Coolest Playlist',
        'description': 'Look it\'s my coolest playlist'
    }
    LOGGER.info(f'\n\nMaking request to {create_playlist_url}\n\n')
    playlist_response_raw = requests.post(create_playlist_url, data=request_body,
                                          headers={'Authorization': f'Bearer {access_token}'})

    if (playlist_response_raw.status_code != 200):
        LOGGER.error(f'\n\nReceived {playlist_response_raw.status_code} response from Spotify playlist create request\n\n{playlist_response_raw.reason}\n\n')
        return None

    playlist_response = playlist_response_raw.json()
    LOGGER.info(f'\n\nSuccessful response from creating playlist: {playlist_response}\n\n')
    return playlist_response['id']


def add_songs_to_playlist(access_token, playlist_id, spotify_tracks):
    add_songs_url = PLAYLIST_ADD_URL_BASE.format(playlist_id)
    request_body = {
        'uris': [track.get('uri') for track in spotify_tracks]
    }
    LOGGER.info(f'\n\nMaking request to {add_songs_url}\n\n')
    add_songs_response_raw = requests.post(add_songs_url, data=request_body,
                                           headers={'Authorization': f'Bearer {access_token}'})

    if (add_songs_response_raw.status_code != 200):
        LOGGER.error(f'Received {add_songs_response_raw.status_code} response from Spotify playlist add songs request{add_songs_response_raw.reason}\n\n')

    add_songs_response = add_songs_response_raw.json()
    LOGGER.info(f'\n\nSuccessful response from adding songs: {add_songs_response}\n\n')
