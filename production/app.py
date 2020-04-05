'''
This is the main progam that runs our backend API. 
Created by Joshua D'Arcy on March 28th, 2020.
'''

import json
import os
import sqlite3
from flask import Flask, redirect, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests

# Bring in environment variables (.env required)
from dotenv import load_dotenv
load_dotenv()

# Modules
from db import init_db_command
from user import User
from Palate import Palate
from Nutrition import Nutrients
from Nutrition import Nutrition_Score
from Recommender import Recommend

#Initialize palate and nutrition modules. 
#Note that the recommender model is not a general init, so have to initialize that one separately.
pal = Palate()
nuts = Nutrients()

# -----------------------------------
# Configuration
# -----------------------------------

GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

# -----------------------------------
# Flask app setup
# -----------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)


# -----------------------------------
# Manage database connection here
# -----------------------------------

# User session management setup
login_manager = LoginManager()
login_manager.init_app(app)

# Naive database setup
try:
    init_db_command()
except sqlite3.OperationalError:
    # Assume it's already been created
    pass

# -----------------------------------
# -----------------------------------
# LOGIN ROUTES
# -----------------------------------
# -----------------------------------

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route("/")
def index():
    if current_user.is_authenticated:
        return (
            "<p>You're logged in, {}! Email: {}</p>"
            "<p>You may now use the endpoints </p>"
            '<a class="button" href="/logout">Logout</a>'.format(
                current_user.name, current_user.email, current_user.profile_pic
            )
        )
    else:
        return '<a class="button" href="/login">Google Login</a>'

#Still need to catch errors if Google doesn't respond
def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information, including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in your db with the information provided by Google
    user = User(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture
    )

    # Doesn't exist? Add it to the database.
    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email, picture)

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("index"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

#Interface for nutrition estimation model
@app.route('/get_nutrients/<string>', methods=['GET'])
@login_required
def return_nutrients(string):
    #Nutrients module has a method called "fast filter" that seeks nutrition value from database
    return nuts.fast_filter(string)

#Interface for nutrition estimation model
@app.route('/get_score/<string>', methods=['GET'])
@login_required
def return_score(string):
    age,gender,activity,food = string.split('|')

    #Nutrients module has a method called "fast filter" that seeks nutrition value from database
    nutrients = nuts.fast_filter(food)
    return Nutrition_Score(int(age), int(gender), int(activity), nutrients).score

#Interface for palate module
@app.route('/get_palate/<string>', methods=['GET'])
@login_required
def return_palate(string):
    #Palate module has a method called "palette_constructor that decomposes foods into their palate signatures"
    stringify = str(pal.palate_constructor(string))
    return stringify

#Interface for recommendation model

@app.route('/get_rec', methods=['POST'])
@login_required
def return_recommendation():
    json_file = request.json
    uhx = json_file["user_hx"]
    ulat = json_file["latitude"]
    ulon = json_file["longitude"]
    udis = json_file["distance"]

    recommendation = Recommend(uhx, ulat, ulon, udis)
    return recommendation.rec_dict

if __name__ == "__main__":
    app.run(ssl_context="adhoc")