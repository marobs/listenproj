from flask import session

SESSION_USER_FIELD = "username"

def get_user_id():
    if (SESSION_USER_FIELD in session):
        return session[SESSION_USER_FIELD]
    else:
        return None

def is_logged_in():
    return SESSION_USER_FIELD in session and session[SESSION_USER_FIELD]

def register_user(username):
    session[SESSION_USER_FIELD] = username
