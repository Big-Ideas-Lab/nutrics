'''
This file defines is the main Flask hub.
Created by Joshua D'Arcy on 4/15/2020.
'''

from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import views, models, resources
import os

#initialize Flask
app = Flask(__name__)
api = Api(app)

#configure sqlalchemy 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24),

#use ORM with SQLAlchemy
db = SQLAlchemy(app)

#create all db tables before accepting first request in Flask
@app.before_first_request
def create_tables():
    db.create_all()

#Assign secret key for JSON Web Tokens (JWT)
app.config['JWT_SECRET_KEY'] = os.urandom(24)
jwt = JWTManager(app)

#Enable the ability to blacklist JWT's -- once a user logs out, we no longer accept their tokens. Prevents nefarious people from stealing tokens.
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']


# Can change time before tokens expire. Shorter times are more secure, longer times are more convenient.
#  Default is 15 minutes and 1 day. 
# app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta()
# app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta()

#Check if token was blacklisted
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)

#convert to user_resources
api.add_resource(resources.UserRegistration, '/registration')
api.add_resource(resources.UserLogin, '/login')
api.add_resource(resources.UserLogoutAccess, '/logout/access')
api.add_resource(resources.UserLogoutRefresh, '/logout/refresh')
api.add_resource(resources.TokenRefresh, '/token/refresh')
api.add_resource(resources.EditPreference, '/edit')
api.add_resource(resources.GetUserPreference, '/prefs')

#convert to recommender_resources
api.add_resource(resources.Recommender, '/recommendation')