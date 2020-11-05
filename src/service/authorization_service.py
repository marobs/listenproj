from dao import token_dao_in_memory as token_dao


def is_authenticated(username):
    return not not token_dao.get_access_token(username)


def get_access_token(username):
    return token_dao.get_access_token(username)


def save_access_token(username, access_token):
    return token_dao.save_access_token(username, access_token)

def get_refresh_token(username):
    return token_dao.get_refresh_token(username)


def save_refresh_token(username, refresh_token):
    return token_dao.save_refresh_token(username, refresh_token)

def clear_authorization_dao():
    token_dao.clear()