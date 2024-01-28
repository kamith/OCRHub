import json
import traceback
import re
from os import environ as env
from urllib.parse import quote_plus, urlencode
from flask import Flask, redirect, render_template, session, url_for, request, abort
from flask_talisman import Talisman
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")
Talisman(app)  # Enables HTTPS and sets security headers

oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={"scope": "openid profile email"},
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

# Helper function to check if user is logged in
def is_logged_in():
    return 'user' in session

# Input Validation Function
def validate_name(name):
    if not re.match("^[a-zA-Z ]*$", name):
        abort(400)  # Bad Request if name is not valid

@app.route("/")
def home():
    return render_template(
        "home.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN") + "/v2/logout?" + urlencode(
            {"returnTo": url_for("home", _external=True), "client_id": env.get("AUTH0_CLIENT_ID")},
            quote_via=quote_plus,
        )
    )

@app.route('/hello', methods=['POST'])
def hello():
    if not is_logged_in():
        return redirect(url_for('login'))

    name = request.form.get('name')
    validate_name(name)  # Input validation
    if name:
        print('Request for hello page received with name=%s' % name)
        return render_template('hello.html', name=name)
    else:
        print('Request for hello page received with no name or blank name -- redirecting')
        return redirect(url_for('home'))

@app.errorhandler(400)
def bad_request(error):
    return render_template("400_error.html"), 400

@app.errorhandler(500)
def internal_error(error):
    error_info = traceback.format_exc()
    print(error_info)
    return render_template("500_error.html", error_info=error_info), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000), ssl_context='adhoc')
