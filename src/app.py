from flask import Flask
import controllers

import service.secrets_service as secrets_service

import argparse

# Initialize Flask app with the template folder address
app = Flask(__name__, template_folder='templates')

app.secret_key = secrets_service.get_secret_key()

# Register the controllers and set the secret key
app.register_blueprint(controllers.listen_controller.listen_controller)
# app.secret_key = helpers.getFlaskSecret()

# Get and set flags
# parser = argparse.ArgumentParser(description="Start up a ltt-to-spotify server.")
# parser.add_argument('-nc', '--nocache', action='store_true', help="Enable to not cache or used cache data")

# Listen on external IPs
# For us, listen to port 3000 so you can just run 'python app.py' to start the server
if __name__ == '__main__':
    # listen on external IPs
    app.run(host='0.0.0.0', port=3000, debug=True, use_reloader=False)
