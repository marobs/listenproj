from flask import *
from flask import request
import logging as LOGGER
from service import session_service
from service import login_service

# Register a blueprint named 'listen_controller'
listen_controller = Blueprint('listen_controller', __name__, template_folder='templates')


##
## [GET] Base index endpoint
## HTML
##
@listen_controller.route('/')
def index():
    print("In GET /")
    user_id = session_service.get_user_id()

    if (user_id is None):
        return redirect(url_for('listen_controller.login'))

    #elif (authorization_service.is_authenticated(user_id) is False):
    #    return redirect(url_for('listen_controller.spotify'))

    else:
        return render_template("index.html")


##
## [GET] Login page endpoint
## HTML
##
@listen_controller.route('/login', methods=['GET'])
def login():
    print("In GET /login")
    if (session_service.is_logged_in()):
        return redirect(url_for('listen_controller.index'))

    return render_template('login.html')


##
## [POST] Login
## JSON
##
@listen_controller.route('/login', methods=['POST'])
def login_route():
    print("In POST /login")
    try:
        username, password = get_login_request_data(request)
        if (login_service.check_user_password(username, password)):
            session_service.register_user(username)
            return redirect('main')

        else:
            render_template('bad_login.html')

    except Exception as ex:
        LOGGER.exception(ex)
        return render_template('bad_login.html')


##
## Misc
##
def get_login_request_data(req):
    data = req.get_json()
    username = data["username"]
    password = data["password"]
    return username, password
