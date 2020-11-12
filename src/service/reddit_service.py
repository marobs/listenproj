import re
import requests
import logging
from datetime import date

from util import song_util
from dao import playlist_dao_in_memory as playlist_dao

LOGGER = logging.getLogger(__name__)

LISTENTOTHIS_URL = 'https://www.reddit.com/r/listentothis/top.json?t=day'
DEFAULT_LTTB_HEADERS = {'user-agent': 'Listen-To-This-Bot'}

split_artist_title_regex = re.compile(r'([\w ]+)-+([\w ]+)')


class RedditException(Exception):
    pass


def get_song_from_post(post_title):
    match = split_artist_title_regex.match(post_title)
    if match and match.lastindex == 2:
        return match[1].strip(), match[2].strip()


def get_reddit_tracks():
    today = date.today().strftime('%Y/%m/%d')
    tracks = playlist_dao.get_playlist_for_date(today)

    if tracks is None:
        tracks = request_songs_from_reddit()
        playlist_dao.add_playlist_for_date(today, tracks)

    return tracks


def request_songs_from_reddit():
    songs_response = requests.get(LISTENTOTHIS_URL, headers=DEFAULT_LTTB_HEADERS)

    validate_response(songs_response)

    tracks = []
    for child in songs_response.json()['data']['children']:
        if 'data' not in child or 'stickied' in child['data'] and child['data']['stickied']:
            continue

        post = child['data']
        try:
            artist, title = get_song_from_post(post['title'])
            tracks.append(song_util.create_track_dict(artist, title, None, None))
        except:
            continue

    LOGGER.info(f'Received Reddit tracks:\n\n{tracks}\n\n')
    return tracks


def validate_response(songs_response):
    if songs_response.status_code != 200:
        LOGGER.error(f'Got {songs_response.status_code} from reddit with url:{songs_response.url}')
        raise RedditException

    songs_response_json = songs_response.json()
    if 'data' not in songs_response_json or 'children' not in songs_response_json['data']:
        LOGGER.error(f'Got response JSON with empty data')
        raise RedditException
