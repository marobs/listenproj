access_tokens = {}
refresh_tokens = {}


def get_access_token(username):
    global access_tokens
    if username in access_tokens:
        return access_tokens[username]
    else:
        return None


def save_access_token(username, access_token):
    global access_tokens
    access_tokens[username] = access_token


def delete_access_token(username):
    global access_tokens
    del access_tokens[username]


def get_refresh_token(username):
    global refresh_tokens
    if username in refresh_tokens:
        return refresh_tokens[username]
    else:
        return None


def save_refresh_token(username, refresh_token):
    global refresh_tokens
    refresh_tokens[username] = refresh_token


def delete_refresh_token(username):
    global refresh_tokens
    del refresh_tokens[username]


def clear():
    global access_tokens, refresh_tokens
    access_tokens = {}
    refresh_tokens = {}
