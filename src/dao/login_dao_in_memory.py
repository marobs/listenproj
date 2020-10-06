passwords = {}

def get_password(user_id):
    if user_id in passwords:
        return passwords[user_id]

    return None

def register_user(user_id, password):
    passwords[user_id] = password