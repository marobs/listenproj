import logging
import requests
from datetime import date
import urllib.parse

from util import song_util
from dao import spotify_user_dao_in_memory as spotify_user_dao
from dao import spotify_track_dao_in_memory as spotify_track_dao

from service import secrets_service, session_service, authorization_service
from constants import SPOTIFY_CLIENT_ID

LOGGER = logging.getLogger(__name__)


class SpotifyException(Exception):
    pass


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
    spotify_user_dao.clear()


def has_spotify_id(username):
    spotify_id = spotify_user_dao.get_user(username)
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
        raise SpotifyException(f'Received response with status code {response.status_code} from Spotify auth endpoint')

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
    today = date.today().strftime('%Y/%m/%d')
    spotify_tracks = spotify_track_dao.get_playlist_for_date(today)

    if spotify_tracks is None:
        spotify_tracks = request_tracks_from_spotify(track_dictionary_list, access_token)
        spotify_track_dao.add_playlist_for_date(today, spotify_tracks)

    LOGGER.info(f'\n\nSpotify tracks post-formatting:\n\n{spotify_tracks}\n\n')
    return spotify_tracks


def request_tracks_from_spotify(track_dictionary_list, access_token):
    spotify_tracks = []

    for track_dictionary in track_dictionary_list:
        spotify_track = search_for_song(track_dictionary['artist'], track_dictionary['title'], access_token)
        if spotify_track is not None:
            spotify_tracks.append(spotify_track)

    return spotify_tracks


def search_for_song(artist, song_title, access_token):
    LOGGER.info(f'\n\nSearching for track {artist} - {song_title}')

    payload = {'q': f'artist:{artist} track:\"{song_title}\"', 'type': 'track', 'limit': '3'}
    params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)
    search_response = requests.get(SEARCH_URL + params, headers={'Authorization': f'Bearer {access_token}'})
    search_response_json = search_response.json()

    if search_response.status_code != 200:
        LOGGER.exception(f'Received {search_response.status_code} response from Spotify search')
        raise SpotifyException(f'Received {search_response.status_code} response from Spotify search')

    if len(search_response_json['tracks']['items']) == 0:
        LOGGER.info(f'No results for Spotify search params: "{payload}"')
        return None

    return get_spotify_track_attributes(search_response.json())


def get_album_art_url(images):
    for image in images:
        if image['height'] == 300:
            return image['url']
    return images[0]['url']

def get_spotify_track_attributes(spotify_response):
    try:
        LOGGER.info(spotify_response['tracks'])
        artist = spotify_response['tracks']['items'][0]['artists'][0]['name']
        title = spotify_response['tracks']['items'][0]['name']
        track_id = spotify_response['tracks']['items'][0]['id']
        uri = spotify_response['tracks']['items'][0]['uri']
        album_art_url = get_album_art_url(spotify_response['tracks']['items'][0]['album']['images'])
        preview_url = spotify_response['tracks']['items'][0]['preview_url']
        return song_util.create_track_dict(artist, title, track_id, uri, album_art_url)
    except:
        LOGGER.exception(f'Error grabbing Spotify song attributes')


#
# Gets the user's Spotify ID based on their access token
#
def get_spotify_id(username, access_token):
    spotify_id = spotify_user_dao.get_user(username)
    if spotify_id is not None:
        return spotify_id

    user_response_raw = requests.get(GET_USER_URL, headers={'Authorization': f'Bearer {access_token}'})
    user_response = user_response_raw.json()

    if user_response_raw.status_code != 200:
        raise SpotifyException(f'Got response code {user_response_raw.status_code} trying to get ID for ' +
                               f'user "{username}"')
    try:
        spotify_id = user_response['id']
        spotify_user_dao.save_spotify_id(username, spotify_id)
        return spotify_id
    except KeyError:
        LOGGER.exception(f'Error grabbing Spotify Id for user {username}')


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
        'name': 'Your Awesome Playlist'
    }
    LOGGER.info(f'\n\nMaking request to {create_playlist_url}\n\n')
    playlist_response_raw = requests.post(create_playlist_url, json=request_body,
                                          headers={'Authorization': f'Bearer {access_token}'})

    if playlist_response_raw.status_code not in (200, 201):
        raise SpotifyException(f'\n\nReceived {playlist_response_raw.status_code} response from ' +
                               f'Spotify playlist create request\n\n{playlist_response_raw.content}\n\n')

    playlist_response = playlist_response_raw.json()
    LOGGER.info(f'\n\nSuccessful response from creating playlist: {playlist_response}\n\n')

    return playlist_response['id']


def add_songs_to_playlist(access_token, playlist_id, spotify_tracks):
    add_songs_url = PLAYLIST_ADD_URL_BASE.format(playlist_id)
    request_body = {
        'uris': [track.get('uri') for track in spotify_tracks]
    }
    LOGGER.info(f'\n\nMaking request to {add_songs_url}\n\n')
    add_songs_response_raw = requests.post(add_songs_url, json=request_body,
                                           headers={'Authorization': f'Bearer {access_token}'})

    if add_songs_response_raw.status_code not in (200, 201):
        raise SpotifyException(f'Received {add_songs_response_raw.status_code} response from Spotify playlist' +
                               f'add songs request{add_songs_response_raw}\n\n')

    add_songs_response = add_songs_response_raw.json()
    LOGGER.info(f'\n\nSuccessful response from adding songs: {add_songs_response}\n\n')
