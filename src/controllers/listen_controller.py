from flask import *

# Register a blueprint named 'listen_controller'
listen_controller = Blueprint('listen_controller', __name__, template_folder='templates')

##
## [GET] Base index endpoint
##
@listen_controller.route('/')
def main_route():
    return render_template("index.html")
