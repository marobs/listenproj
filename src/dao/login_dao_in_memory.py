passwords = {}


def get_password(username):
    if username in passwords:
        return passwords[username]
    return None


def register_user(username, password):
    passwords[username] = password
