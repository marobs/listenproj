import random
import string
FLASK_SECRET_KEY_LENGTH = 16

spotify_secret_key = ''
flask_secret_key = ''

def initialize_spotify_secret_key():
    global spotify_secret_key
    with open('../secret_key.txt') as secret_key_path:
        spotify_secret_key = secret_key_path.readline()


def get_spotify_secret_key():
    global spotify_secret_key
    if not spotify_secret_key:
        initialize_spotify_secret_key()

    return spotify_secret_key


def initialize_flask_secret_key():
    global flask_secret_key
    flask_secret_key = ''.join(random.SystemRandom().choice(string.ascii_letters) for _ in range(16))
    return flask_secret_key


def get_flask_secret_key():
    global flask_secret_key
    if not flask_secret_key:
        initialize_flask_secret_key()

    return flask_secret_key
