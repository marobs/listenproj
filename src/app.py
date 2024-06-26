from flask import Flask
import controllers
from service import login_service, authorization_service, spotify_service

import service.secrets_service as secrets_service


# logging.getLogger("requests").setLevel(logging.INFO)
# logging.getLogger("urllib3").setLevel(logging.INFO)

# Initialize Flask app with the template folder address
app = Flask(__name__, template_folder="templates")

app.secret_key = secrets_service.get_flask_secret_key()

# Register the controllers and set the secret key
app.register_blueprint(controllers.listen_controller.listen_controller)

print("Clearing daos")
login_service.clear_login_dao()
authorization_service.clear_authorization_dao()
spotify_service.clear_spotify_dao()

# Listen on external IPs
# For us, listen to port 3000 so you can just run 'python app.py' to start the server
if __name__ == "__main__":
    # listen on external IPs
    app.run(host="0.0.0.0", port=3000, debug=True, use_reloader=False)
