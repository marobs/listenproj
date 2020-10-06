from dao import token_dao_in_memory as token_dao


def is_authenticated(user_id):
    return is_not_empty(token_dao.get_access_token(user_id))


def is_not_empty(string):
    return string is not None and string
