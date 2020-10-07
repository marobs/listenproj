from dao import login_dao_in_memory as login_dao
from werkzeug.security import check_password_hash, generate_password_hash

class RegistrationException(Exception):
    pass

def check_user_password(user_id, password):
    stored_password = login_dao.get_password(user_id)

    if check_password_hash(stored_password, password):
        return True
    else:
        return False

def register_user(username, password):
    login_dao.register_user(username, generate_password_hash(password))


def validate_registration(username, password, confirm_password):
    if not password == confirm_password:
        raise RegistrationException
