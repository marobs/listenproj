from unittest import mock, TestCase
from unittest.mock import patch, Mock, MagicMock

from werkzeug.security import generate_password_hash

from dao import login_dao_in_memory as login_dao
from service import login_service
from service.login_service import RegistrationException


class Test(TestCase):
    def test_check_user_password_ok(self):
        login_dao.get_password = Mock(return_value=generate_password_hash('password'))
        self.assertTrue(login_service.check_user_password('username', 'password'))

    def test_check_user_password_wrong_password(self):
        login_dao.get_password = Mock(return_value=generate_password_hash('password'))
        self.assertFalse(login_service.check_user_password('username', 'different password'))

    def test_check_user_password_user_doesnt_exist(self):
        login_dao.register_user = Mock(return_value=None)
        login_service.register_user('username', 'password')
        self.assertTrue(login_dao.register_user.called)

    def test_validate_registration_ok(self):
        login_service.validate_registration('password', 'password')

    def test_validate_registration_passwords_not_equal(self):
        with self.assertRaises(RegistrationException):
            login_service.validate_registration('password', 'different password')
