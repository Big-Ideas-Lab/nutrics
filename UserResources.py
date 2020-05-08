'''
This file defines the user resources used by the Flask application.
Created by Joshua D'Arcy on 4/15/2020.
'''

import env #import env.py and os to access env variables
import os
#flask imports
from flask_restful import Resource #access resource API through Flask
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_current_user) #JSON Web token helpers
from flask_mail import Message #import message for emailing authentication links
from flask import url_for #Flask module that creates clickable links (to send to emails)

#local imports
from UserModel import UserModel
from RevokedTokenModel import RevokedTokenModel
from PreferenceModel import PreferenceModel
from FoodModel import FoodModel

from utilities.request_parsers import u_parser, p_parser, a_parser, r_parser, e_parser, f_parser #abstracted out parser logic to different file
from utilities.natural_language import Distance #Distance class is a cosine similarity metric implemented in numpy
from utilities.natural_language import Embed #Embed class palatizes items to give them a 30 dim representation
from Recommender import Recommendations #Recommendation model logic was abstracted out
from run import app, mail #import Flask App and Mail from run file

#general python helpers
from datetime import datetime
import json

#Register users
class UserRegistration(Resource):
    def post(self): #this method (a "Resource" receives post calls to the /registration endpoint defined in run.py
        data = u_parser.parse_args()

        if UserModel.find_by_username(data['username']): #check if username is already taken
            return {'message': 'Username "{}" is already taken. Please choose another username.'.format(data['username'])}
        
        if UserModel.find_by_email(data['email']): #check if email is already used for another account
            return {'message': 'Email address "{}" is already taken. Please enter a different email address.'.format(data['email'])}

        #UserModel defined in models.py
        new_user = UserModel(
            username = data['username'],
            password = UserModel.generate_hash(data['password']),
            email = data['email'],
            age = data['age'], 
            gender_identity = data['gender_identity'],
            activity_level = data['activity_level'],
            admin = False,
            registered_on = datetime.now(), 
            confirmed = False, 
            confirmed_on = None
        )
        
        try:
            new_user.save_to_db()
        except:
            return {'message': 'There was an error saving the user to the database. Please try again.'}, 500
        
        registration_token =  UserModel.generate_confirmation_token(new_user.email) #generate a confirmation token
        clickable = url_for('emailverification', token = registration_token, _external = True) #generate a clickable URL that is sent via email

        #build authentication email
        msg = Message(
            subject='Verification link for nutrics',
            recipients=[new_user.email],
            body=clickable,
            sender=app.config['MAIL_DEFAULT_SENDER']
            )

        try:
            mail.send(msg) #send authentication email
            return {
                'message': 'User {} was created. Validation link sent to email.'.format(new_user.username),
                'email_sent_to': new_user.email
                }
        except:
            return {'message': 'Something went wrong with user registration.'}, 500

#verify a user's email requested in UserRegistration
class EmailVerification(Resource):
    def get(self): #get call with clickable link generated earlier
        data = e_parser.parse_args()
        token = data['token'] #get token from link
        try: 
            email = UserModel.confirm_token(token) #confirm this is the token we generated earlier in UserRegistration
        except:
            return {'message': 'Token is invalid or expired.'}

        user = UserModel.find_by_email(email) #check if user has already been confirmed
        if user.confirmed:
            return {'message': 'User has already been confirmed. Please login.'}
        
        else: #if user not already confirmed, change to True and add a timestamp
            user.confirmed = True
            user.confirmed_on = datetime.now()
            user.save_to_db()
            return {'message':'Congrats! You can now log in.'}

#Login users and start session with access / refresh keys
class UserLogin(Resource):
    def post(self):
        data = u_parser.parse_args()
        current_user = UserModel.find_by_username(data['username']) #get username from call

        if not current_user: #Check that user exists
            return {'message': 'User {} doesn\'t exist. Are you trying to register? Go to the /registration endpoint.'.format(data['username'])}
        
        if not current_user.confirmed: #Check that user is confirmed via email link
            return {'message': 'You need to register your email.'}
            
        if UserModel.verify_hash(data['password'], current_user.password): #check hashed password 
            access_token = create_access_token(identity = data['username']) #generate access token
            refresh_token = create_refresh_token(identity = data['username']) #generate refresh token
            
            if current_user.admin == True: #check if admin privelages are granted
                return {
                    'message': 'Logged in as {}. (admin)'.format(current_user.username),
                    'access_token': access_token,
                    'refresh_token': refresh_token
                    }
            else: #else default to user privelages
                return {
                    'message': 'Logged in as {} (user)'.format(current_user.username),
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
        else: #if password not recognized, send back error message
            return {'message': 'Something went wrong. Please check your password.'}

#Logout users and blacklist tokens so they can no longer be used (requires a re-login).
class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked. You will be unable to use this token in the future.'}
        except:
            return {'message': 'Something went wrong with revoking your access token. Please try again.'}, 500

#Logout user using refresh token (versus the above access token)
class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked. You will be unable to use this token in the future.'}
        except:
            return {'message': 'Something went wrong with revoking your refresh token. Please try again.'}, 500

#create a new access token when given non-revoked refresh token by user
class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity() #find user info from JSON Web token
        access_token = create_access_token(identity = current_user) #create a new access token
        return {'access_token': access_token, 
        'message': 'Your access token was generated by using a refresh token.'
        }

#Class to edit food preferences. Option to either add or remove.
class EditPreference(Resource): 
    @jwt_required
    def post(self):
       
        data = p_parser.parse_args() #use parser to get data from JSON
        pref = data['preference'] #preference param is the name of the food item the user enjoys
        action = data['preference_action'] #preference action param is either "add" or "remove"
        added = datetime.now() #timestamp so we can track history and changes over time
        user = get_jwt_identity() #get user identity from JSON web token
        new_pref = PreferenceModel(username = user, preference = pref, added = added)  #Instantiate a Preference from models.PreferenceModel 

        #action needs to be defined in the original post call. Add adds one. Remove removes all matching rows. 
        if action == 'add':
            try:
                new_pref.save_to_db()
                return {'message': '{} successfully added for {}.'.format(pref, user)}, 200
            except:
                return {'message': 'There was a problem adding to the preferences database.'}, 500
         
        if action == "remove":
            try: 
                new_pref.remove_from_db()
                return {'message': '{} successfully removed from {}.'.format(pref, user)}, 200
            except:
                return {'message': 'There was a problem removing the item from the preferences database.'}, 500

        else: 
            return {'message': 'preference_action parameter must include either "add" or "remove"'}

#Class to gather all known preferences for a given user. Users need access to this endpoint to update their preferences. 
#Users can only collect their own preferences. This is in contrast to the admin method defined in admin_resources.py
class GetUserPreference(Resource):
    @jwt_required
    def get(self):
        username = get_jwt_identity() #get username from token
        return PreferenceModel.return_user_hx(username) 

#POST call with latitude and longitude, returns recommendation based on user session.
class Recommender(Resource): 
    @jwt_required
    def post(self):
        data = r_parser.parse_args() #pull out latitude, longitude, and distance from post call. Convert to floats immediately.
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        distance = float(data['distance'])
        username = get_jwt_identity() #access user from indexed JSON web token. Need user information for recommendation model.
        
        recs = Recommendations.match(username, latitude, longitude, distance)  #use Recommender Module

        return {'data': json.dumps(recs)} #return data