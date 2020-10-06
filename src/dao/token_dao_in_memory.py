access_tokens = {}
refresh_tokens = {}

def get_access_token(user_id):
    if (user_id in access_tokens):
        return access_tokens[user_id]
    else:
        return None

def save_access_token(user_id, access_token):
    access_tokens[user_id] = access_token

def delete_access_token(user_id):
    del access_tokens[user_id]