from dao import spotify_token_dao_in_memory as spotify_token_dao


def is_authenticated(username):
    return not not spotify_token_dao.get_access_token(username)


def get_access_token(username):
    return spotify_token_dao.get_access_token(username)


def save_access_token(username, access_token):
    return spotify_token_dao.save_access_token(username, access_token)


def get_refresh_token(username):
    return spotify_token_dao.get_refresh_token(username)


def save_refresh_token(username, refresh_token):
    return spotify_token_dao.save_refresh_token(username, refresh_token)


def clear_authorization_dao():
    spotify_token_dao.clear()
