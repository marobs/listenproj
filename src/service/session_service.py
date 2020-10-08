import random
import string

from flask import session

SESSION_USER_FIELD = "username"
SESSION_STATE_FIELD = "state"
STATE_STRING_LENGTH = 16

def get_username():
    if (SESSION_USER_FIELD in session):
        return session[SESSION_USER_FIELD]
    else:
        return None

def is_logged_in():
    return SESSION_USER_FIELD in session and session[SESSION_USER_FIELD]

def register_user(username):
    session[SESSION_USER_FIELD] = username

def get_state():
    if SESSION_STATE_FIELD not in session:
        session[SESSION_STATE_FIELD] = generate_state_string()

    return session[SESSION_STATE_FIELD]

def generate_state_string():
    return ''.join(random.SystemRandom().choice(string.ascii_letters) for _ in range(STATE_STRING_LENGTH))
