import requests
import logging

LOGGER = logging.getLogger(__name__)

LISTENTOTHIS_URL = 'https://www.reddit.com/r/listentothis/top.json?t=day'

class RedditException(Exception):
    pass

def get_songs():
    songs_response = requests.get(LISTENTOTHIS_URL, headers={'user-agent': 'Chrome/85.0'})

    if songs_response.status_code != 200:
        LOGGER.error(f'Got {songs_response.status_code} from reddit with url:{songs_response.url}')
        raise RedditException

    response_json = songs_response.json()
    if 'data' not in response_json or 'children' not in response_json['data']:
        LOGGER.error(f'Got response JSON with empty data')
        raise RedditException

    songs = []
    for post in response_json['data']['children']:
        if 'data' not in post or 'stickied' in post['data'] and post['data']['stickied']:
            continue
        print(post['data']['title'])
