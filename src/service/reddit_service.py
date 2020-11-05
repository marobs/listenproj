import re
import requests
import logging
from util import song_util

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
    songs_response = requests.get(LISTENTOTHIS_URL, headers=DEFAULT_LTTB_HEADERS)

    validate_response(songs_response)

    tracks = []
    for child in songs_response.json()['data']['children']:
        if 'data' not in child or 'stickied' in child['data'] and child['data']['stickied']:
            continue

        post = child['data']
        try:
            artist, title = get_song_from_post(post['title'])
            tracks.append(song_util.create_artist_song_dict(artist, title))
        except:
            continue

    return tracks


def validate_response(response):
    if response.status_code != 200:
        LOGGER.error(f'Got {songs_response.status_code} from reddit with url:{songs_response.url}')
        raise RedditException

    response_json = response.json()
    if 'data' not in response_json or 'children' not in response_json['data']:
        LOGGER.error(f'Got response JSON with empty data')
        raise RedditException
