from flask import *

# Register a blueprint named 'main'
sample = Blueprint('sample', __name__, template_folder='templates')

##
## [GET] Base index endpoint
##
@sample.route('/sample')
def sample_route():
    return render_template("index.html")