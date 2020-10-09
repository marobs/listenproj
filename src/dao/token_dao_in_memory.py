access_tokens = {}
refresh_tokens = {}

def get_access_token(username):
    if (username in access_tokens):
        return access_tokens[username]
    else:
        return None

def save_access_token(username, access_token):
    access_tokens[username] = access_token

def delete_access_token(username):
    del access_tokens[username]

def get_refresh_token(username):
    if (username in refresh_tokens):
        return refresh_tokens[username]
    else:
        return None

def save_refresh_token(username, refresh_token):
    refresh_tokens[username] = refresh_token

def delete_refresh_token(username):
    del refresh_tokens[username]