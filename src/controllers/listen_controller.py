from flask import *
from flask import request
import logging as LOGGER

from service import session_service, spotify_service, authorization_service, login_service, reddit_service

# Register a blueprint named 'listen_controller'
listen_controller = Blueprint('listen_controller', __name__, template_folder='templates')


##
## [GET] Base index endpoint
## HTML
##
@listen_controller.route('/')
def index():
    print("In GET /")
    username = session_service.get_username()

    if (username is None):
        return redirect(url_for('listen_controller.login'))

    elif (authorization_service.is_authenticated(username) is False):
        return redirect(spotify_service.create_spotify_request_url())

    else:
        return render_template("index.html", login=username)


##
## [GET] Login page endpoint
## HTML
##
@listen_controller.route('/login', methods=['GET'])
def login():
    print("In GET /login")
    if (session_service.is_logged_in()):
        return redirect('/')

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
            return redirect('/')

        else:
            render_template('bad_login.html')

    except Exception as ex:
        LOGGER.exception(ex)
        return render_template('bad_login.html')


##
## [GET] Register
## HTML
##
@listen_controller.route('/register', methods=['GET'])
def register_route():
    return render_template('register.html')


##
## [POST] Register
## JSON
##
@listen_controller.route('/register', methods=['POST'])
def register():
    try:
        username, password, confirm = get_register_request_data(request)

        login_service.validate_registration(username, password, confirm)
        login_service.register_user(username, password)
    except Exception as ex:
        LOGGER.exception(ex)
        return render_template('bad_login.html')
    return redirect('/')

##
## [GET] Register
## HTML
##
@listen_controller.route('/callback', methods=['GET'])
def callback():
    authorization_code = request.args.get('code')
    state_string = request.args.get('state')

    if not state_string == session_service.get_state():
        LOGGER.error(f'returned state string not equal to user state string:\n{state_string}  :  {session_service.get_state()}')
        return render_template('error.html')

    spotify_service.first_time_spotify_authorization(authorization_code, session_service.get_username())

    LOGGER.info('called back')
    return render_template('index.html', login=session_service.get_username())


@listen_controller.route('/reddit', methods=['GET'])
def reddit():
    username = session_service.get_username()
    access_token = authorization_service.get_access_token(username)

    reddit_tracks = reddit_service.get_reddit_tracks()
    spotify_tracks = spotify_service.get_spotify_tracks(reddit_tracks, access_token)
    return render_template('reddit.html', tracks=reddit_tracks)


##
## Misc
##
def get_login_request_data(req):
    username = req.form.get("username")
    password = req.form.get("password")
    return username, password


def get_register_request_data(req):
    username = req.form.get("username")
    password = req.form.get("password")
    confirm = req.form.get("confirmed_password")
    return username, password, confirm
