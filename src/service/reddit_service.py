import re
import requests
import logging

LOGGER = logging.getLogger(__name__)

LISTENTOTHIS_URL = 'https://www.reddit.com/r/listentothis/top.json?t=day'

split_artist_title_regex = re.compile(r'([\w ]+)-+([\w ]+)')

class RedditException(Exception):
    pass


def get_song_from_post(post_title):
    match = split_artist_title_regex.match(post_title)
    if match and match.lastindex == 2:
        return match[1].strip(), match[2].strip()


def get_songs():
    songs_response = requests.get(LISTENTOTHIS_URL, headers={'user-agent': 'Listen-To-This-Bot'})

    if songs_response.status_code != 200:
        LOGGER.error(f'Got {songs_response.status_code} from reddit with url:{songs_response.url}')
        raise RedditException

    response_json = songs_response.json()
    if 'data' not in response_json or 'children' not in response_json['data']:
        LOGGER.error(f'Got response JSON with empty data')
        raise RedditException

    song_titles = []
    for child in response_json['data']['children']:
        if 'data' not in child or 'stickied' in child['data'] and child['data']['stickied']:
            continue
        post = child['data']
        try:
            artist, title = get_song_from_post(post['title'])
            song_titles.append(title)
        except:
            continue

    return song_titles
