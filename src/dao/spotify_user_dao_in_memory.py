import logging

spotify_users = {}

LOGGER = logging.getLogger(__name__)


def get_user(username):
    global spotify_users
    if (username in spotify_users):
        return spotify_users[username]
    else:
        return None

def save_spotify_id(username, spotify_id):
    LOGGER.info(f'Saving spotify_id {spotify_id} for username {username}')
    global spotify_users
    spotify_users[username] = spotify_id

def delete_spotify_id(username):
    global spotify_users
    del spotify_users[username]

def clear():
    global spotify_users
    spotify_users = {}
