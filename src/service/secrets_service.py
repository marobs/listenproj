secret_key = ''

def initialize_secret_key():
    global secret_key
    with open('../secret_key.txt') as secret_key_path:
        secret_key = secret_key_path.readline()

def get_secret_key():
    if not secret_key:
        initialize_secret_key()

    return secret_key
