'''
This file defines the main Flask hub.
Created by Joshua D'Arcy on 4/15/2020.
'''

import env #env is a .py file in the directory that creates the variables accessed by os.getenv
import os #get access to environment variables
from flask import Flask #import flask apps
from flask_restful import Api #API organization
from flask_sqlalchemy import SQLAlchemy #Connect to SQLite3 database
from flask_jwt_extended import JWTManager #Required for JSON web token use
from flask_mail import Mail #For email authentication
from flask_mail import Message #For email authentication
from datetime import datetime #For timing 

#initialize Flask
app = Flask(__name__)
api = Api(app)

#configure Flask
app.config['SECURITY_PASSWORD_SALT'] = os.getenv('FLASK_SECRET_SALT')

# configure sqlalchemy to use a local sqlite3 file. 
# SQLite3 is not persistent in a Docker container, so consider a MySQL server or a managed service through Google, AWS, or RedCap. 
# If you want to use MySQL or Postgres, just swap out the URI. Flask-SQLAlchemy should handle the rest. 
# The rest of the API was built to handle a switch to another db server (generic SQL calls, consistent db methods, etc). 
# SQLite3 is easiest to manage for development, so I would recommend it's use prior to scaled production.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('APP_SECRET')

#use ORM with SQLAlchemy (https://auth0.com/blog/sqlalchemy-orm-tutorial-for-python-developers/)
db = SQLAlchemy(app)

# Configure email features
# We use these configs to set up a sender email for email authentication.
# Later, you can use this email authentication to reset passwords, identify identity, etc.
# I created a google account with BIG IDEAS Lab branding for this purpose. Please refer to env.py for more details.
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')
mail = Mail(app)

#import models and resources down here to prevent circular imports
import UserResources, AdminResources
from UserModel import UserModel
from RevokedTokenModel import RevokedTokenModel

#create all db tables before accepting first request in Flask. These tables are defined in models.py.
@app.before_first_request
def create_tables():
    db.create_all()

    # Create admin using UserModel
    # init admin using environment variables from env.py.
    if not UserModel.find_by_username('administrator'):
        admin = UserModel(
            email = os.getenv('ADMIN_EMAIL'),
            username = os.getenv('ADMIN_USERNAME'),
            password = UserModel.generate_hash(os.getenv('ADMIN_PASSWORD')),
            age = 99, 
            activity_level = 1, 
            gender_identity = 1,
            admin = True,
            registered_on = datetime.now(),
            confirmed = True,
            confirmed_on = datetime.now()
        )
        #don't forget to actually save and commit to db!
        admin.save_to_db()

#Assign secret key for JSON Web Tokens (JWT)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET')
jwt = JWTManager(app)

# Enable the ability to blacklist JWT's -- once a user logs out, we no longer accept their tokens. 
# Helps prevent nefarious people from stealing tokens with interception methods.
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']


#method to check if token was blacklisted.
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return RevokedTokenModel.is_jti_blacklisted(jti)

#Each resource endpoint points to a class (defined with a POST or GET method) in user_resources.py
#user_resources. More information in user_resources.py. 
api.add_resource(UserResources.UserRegistration, '/registration') #Register user endpoint
api.add_resource(UserResources.UserLogin, '/login') #User AND admin login endpoint
api.add_resource(UserResources.UserLogoutAccess, '/logout/access') #User AND admin logout endpoint with an access token
api.add_resource(UserResources.UserLogoutRefresh, '/logout/refresh') #User AND admin logout endpoint with refresh token
api.add_resource(UserResources.TokenRefresh, '/token/refresh') #User refresh token endpoint
api.add_resource(UserResources.EditPreference, '/editpreferences') #User endpoint to edit their preferences
api.add_resource(UserResources.GetUserPreference, '/preferences') #User endpoint to list all of their preferences
api.add_resource(UserResources.EmailVerification, '/verification') #user endpoint for email verification 
api.add_resource(UserResources.Recommender, '/recommendation') #user endpoint for local nutrition recommendations

#admin resources. More information in admin_resources.py
api.add_resource(AdminResources.AdminUserInfo, '/admin/user/info') #Admin endpoint to collect all users
api.add_resource(AdminResources.AdminUserPreferences, '/admin/user/preferences') #Admin endpoint to view all user preferences
api.add_resource(AdminResources.AdminAccess, '/admin/access') #Admin endpoint to add admin privelages to other users
api.add_resource(AdminResources.AdminFoodDump, '/admin/food/dump') #Admin endpoint to data dump all foods in database
api.add_resource(AdminResources.AdminFoodAdd, '/admin/food/add') #Admin endpoint to add food items to database
api.add_resource(AdminResources.AdminFoodEdit, '/admin/food/edit') #Admin endpoint to edit or remove food items in database
api.add_resource(AdminResources.AdminFoodRemove, '/admin/food/remove') #Admin endpoint to edit or remove food items in database