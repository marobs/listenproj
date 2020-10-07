from flask import Flask
import controllers

import argparse

# Initialize Flask app with the template folder address
app = Flask(__name__, template_folder='templates')

try:
    fp = open('secret_key.txt')
    app.secret_key = fp.readline()
except:
    raise Exception('secret_key.txt not found')
finally:
    fp.close()

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
    app.run(host='localhost', port=8000, debug=True, use_reloader=False)