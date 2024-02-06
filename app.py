import json
import traceback
import re
import base64
import os
import sass
from os import environ as env
from urllib.parse import quote_plus, urlencode
from flask import Flask, redirect, render_template, session, url_for, request, abort
from authlib.integrations.base_client.errors import OAuthError
from flask_talisman import Talisman
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")
Talisman(app)  # Enables HTTPS and sets security headers
has_run_once = False

# Initialize OAuth with Okta configuration using Auth0 variable names
oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"), # Replace with OKTA_CLIENT_ID after updating environment variables
    client_secret=env.get("AUTH0_CLIENT_SECRET"), # Replace with OKTA_CLIENT_SECRET after updating environment variables
    client_kwargs={"scope": "openid profile email"},
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration', # Replace AUTH0_DOMAIN with your Okta domain
)

def compile_scss():
    """Compiles SCSS files into CSS at the specified directory."""
    input_dir = os.path.join(app.static_folder, 'scss')  # Path to your SCSS files
    output_dir = os.path.join(app.static_folder, 'css')  # Path where CSS files should go
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for scss_file in os.listdir(input_dir):
        if scss_file.endswith('.scss'):
            input_file_path = os.path.join(input_dir, scss_file)
            output_file_path = os.path.join(output_dir, scss_file.replace('.scss', '.css'))
            css_content = sass.compile(filename=input_file_path)
            with open(output_file_path, 'w') as file:
                file.write(css_content)
    print("SCSS files compiled successfully.")

@app.before_request
def before_first_request():
    global has_run_once
    if not has_run_once:
        # Your code here, e.g., compile_scss()
        print("Running once before the first request.")
        has_run_once = True
        compile_scss()

# Helper function to check if user is logged in
def is_logged_in():
    return 'user' in session

# Input Validation Function
def validate_name(name):
    if not re.match("^[a-zA-Z ]*$", name):
        abort(400)  # Bad Request if name is not valid

@app.route("/")
def landing_page():
    return render_template(
        "landing_page.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
    )

# #temp route for testing
# @app.route("/")
# def landing_page():
#     # Redirect to the selection page instead of rendering home.html
#     return redirect(url_for('selection_page'))
        
     

def generate_nonce(length=16):
    """Generate a random string for nonce."""
    return base64.urlsafe_b64encode(os.urandom(length)).decode('utf-8')

@app.route("/login")
def login():
    nonce = generate_nonce()
    session['nonce'] = nonce  # Store nonce in session
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True),
        nonce=nonce
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    try:
        # Process the OAuth callback and extract the user info from the token
        token = oauth.auth0.authorize_access_token()
        nonce = session.get('nonce')  # Retrieve nonce from session
        user_info = oauth.auth0.parse_id_token(token, nonce)
        
        # Store the user info in the session
        session["user"] = user_info

        # Redirect to the selection hub page instead of the landing page
        return redirect(url_for('selection_page'))
    except OAuthError as error:
        print(f"OAuthError: {error.error}: {error.description}")
        return redirect(url_for('unauthorized'))


@app.route("/logout")
def logout():
    session.clear()
    params = {"returnTo": url_for("ocr_hub_landing_page", _external=True), "client_id": env.get("AUTH0_CLIENT_ID")}
    return redirect(
        f'https://{env.get("AUTH0_DOMAIN")}/v2/logout?' + urlencode(params, quote_via=quote_plus)
    )

@app.route('/selection_page', methods=['GET', 'POST'])
def selection_page():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        validate_name(name)  # Input validation
    else:
        # Default behavior for GET request
        name = session.get("user", {}).get("name", "Guest")
    
    return render_template('selection_hub.html', name=name)

@app.route('/ocr_chat', methods=['POST'])
def ocr_chat():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    selected_option = request.form.get('selected_option')
    # Now, you can use the selected_option to do whatever is needed on the ocr_chat page
    return render_template('ocr_chat.html', selected_option=selected_option)

@app.errorhandler(400)
def bad_request(error):
    return render_template("400_error.html"), 400

@app.errorhandler(500)
def internal_error(error):
    error_info = traceback.format_exc()
    print(error_info)
    return render_template("500_error.html", error_info=error_info), 500

@app.route("/unauthorized")
def unauthorized():
    # Render the unauthorized.html template instead of returning a simple string
    return render_template("unauthorized.html"), 403

if __name__ == "__main__":
    app.run(host="localhost", port=3000, ssl_context='adhoc')