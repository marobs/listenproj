passwords = {}


def get_password(username):
    global passwords
    if username in passwords:
        return passwords[username]
    return None


def register_user(username, password):
    global passwords
    passwords[username] = password


def clear():
    global passwords
    passwords = {}
    print(f'login dao passwords: {passwords}')
