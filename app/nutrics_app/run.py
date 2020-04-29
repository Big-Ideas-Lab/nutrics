'''
This file defines is the main Flask hub.
Created by Joshua D'Arcy on 4/15/2020.
'''
#get access to environment variables
import env
import pymysql
#import flask apps
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_mail import Message
import os
from datetime import datetime
#initialize Flask
app = Flask(__name__)
api = Api(app)

#configure Flask
app.config['SECURITY_PASSWORD_SALT'] = 'supersecret'

#configure sqlalchemy for mysql in parallel docker. From docker docs https://docs.docker.com/compose/networking/
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@db:3306/users'

#configure sqlalchemy to just use a local sqlite3 file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecret',

#configure mail
# After 'Create app'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')
mail = Mail(app)


#use ORM with SQLAlchemy
db = SQLAlchemy(app)

import views, models, resources

#create all db tables before accepting first request in Flask
@app.before_first_request
def create_tables():
    db.create_all()

    if not models.UserModel.find_by_username('administrator'):
        # Create admin using the above model
        admin = models.UserModel(
            email = 'joshuadrc@gmail.com',
            username = 'administrator',
            password = models.UserModel.generate_hash('Admin10!'),
            age = 26, 
            activity_level = 2, 
            gender_identity = 1,
            admin = True,
            registered_on = datetime.now(),
            confirmed = True,
            confirmed_on = datetime.now()
        )
        admin.save_to_db()

#Assign secret key for JSON Web Tokens (JWT)
app.config['JWT_SECRET_KEY'] = 'alsosecretkey'
jwt = JWTManager(app)

#Enable the ability to blacklist JWT's -- once a user logs out, we no longer accept their tokens. Prevents nefarious people from stealing tokens.
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

# Can change time before tokens expire. Shorter times are more secure, longer times are more convenient.
#  Default is 15 minutes and 1 day. 
# app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta()
# app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta()
# import views, models, resources


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
api.add_resource(resources.Admin, '/admin')
api.add_resource(resources.EmailVerification, '/verification')

        #convert to recommender_resources
api.add_resource(resources.Recommender, '/recommendation')
# if __name__ == "__main__":
#     app.run("0.0.0.0", port=5001, debug=True)