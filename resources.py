'''
This file defines the resources used by the Flask application.
Created by Joshua D'Arcy on 4/15/2020.
'''

#flask imports
from flask_restful import Resource, reqparse
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_current_user)
# from flask_user import roles_required
from datetime import datetime

#local imports
from models import UserModel, RevokedTokenModel, PreferenceModel
from local import nutrics_db
from Palate import Palate
pal = Palate()

#cosine and json
from scipy.spatial.distance import cosine
import json

#create parser for incoming user data
u_parser = reqparse.RequestParser()
u_parser.add_argument('username', help = 'Username cannot be blank.', required = True)
u_parser.add_argument('password', help = 'Please enter a valid password.', required = True)
u_parser.add_argument('role', help = 'Sorry, that is not a valid role. Please enter "admin" or "user".', required = True)

#create parser for incoming geolocal data
r_parser = reqparse.RequestParser()
r_parser.add_argument('latitude', help= 'Latitude parameter is required.', required = True)
r_parser.add_argument('longitude', help= 'Longitude paramter is required.', required = True)

#Preference parser
p_parser = reqparse.RequestParser()
p_parser.add_argument('preference', help = 'This field cannot be blank', required = True)
p_parser.add_argument('preference_action', help = 'This field cannot be blank', required = True)

#Admin parser
a_parser = reqparse.RequestParser()
a_parser.add_argument('action', help = 'This field cannot be blank', required = True)
a_parser.add_argument('new_admin', help = 'This field only needs to be filled when adding new admin.', required = False)

#Approved list
pre_approved = ['joshua', 'jessilyn']

#Register users
class UserRegistration(Resource):
    def post(self):
        data = u_parser.parse_args()
        
        if UserModel.find_by_username(data['username']):
            return {'message': 'Username "{}" is already taken. Please choose another username.'.format(data['username'])}
        
        new_user = UserModel(
            username = UserModel.generate_hash(data['username')],
            password = UserModel.generate_hash(data['password']),
            role = data['role'],
            joined = str(datetime.utcnow())
        )
        
        if new_user.role == 'admin' and new_user.username not in pre_approved:
            return {
                'message': 'You selected admin as a role, but are not on our approved list. Please email jessilyn.dunn@duke.edu for access.'
            }
        #for better security, can limit refresh delta for refresh token. Or get rid of refresh priveleges altogether.
        try:
            new_user.save_to_db()
            access_token = create_access_token(identity = data['username'])
            refresh_token = create_refresh_token(identity = data['username'])
            return {
                'message': 'User {} was created with {} priveleges.'.format(data['username'], data['role']),
                'access_token': access_token,
                'refresh_token': refresh_token
                }
        except:
            return {'message': 'Something went wrong with user registration.'}, 500

#todo: Need to build a method to reset / change password. Will require Flask - security (and an email?)
#Login users and start session with access / refresh keys. Draws from models.UserModel
class UserLogin(Resource):
    def post(self):
        data = u_parser.parse_args()
        current_user = UserModel.find_by_username(data['username'])

        if not current_user:
            return {'message': 'User {} doesn\'t exist. Are you trying to register? Go to the /registration endpoint.'.format(data['username'])}
        
        if UserModel.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity = data['username'])
            refresh_token = create_refresh_token(identity = data['username'])
            return {
                'message': 'Logged in as {} ({}).'.format(current_user.username, current_user.role),
                'access_token': access_token,
                'refresh_token': refresh_token
                }
        else:
            return {'message': 'Something went wrong. Please check your password.'}

#Logout users and blacklist tokens. Adds to models.RevokedTokenModel
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

#Logout user using refresh token. Adds to models.RevokedTokenModel
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
#todo: write function to access how much longer remaining for refresh token life. Default is 1 day.
class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token, 
        'message': 'Your access token was generated by using a refresh token.', 
        'days_remaining_for_refresh': 1
        }

class Admin(Resource):
    @jwt_required
    def post(self):
        #get data from post call
        data = a_parser.parse_args()
        action = data['action']
        new_admin = data['new_admin']
        #check user JWT
        current_user = get_jwt_identity()
        row = UserModel.find_by_username(current_user)
        #verify user with JWT is an admin via role column
        if 'admin' not in row.role:
            return {"msg": "Forbidden, your role is {}".format(row.role)}, 403
        else:
            if action == 'get_users':
                return UserModel.return_all_users()
            if action == 'get_preferences':
                return PreferenceModel.data_dump()
            if action == 'add_admin':
                pre_approved.append(new_admin)
                return {'message': 'Future user {} given admin privelage. Have them register now.'.format(new_admin)}


#Class to edit preferences
class EditPreference(Resource): 
    @jwt_required
    def post(self):

        #use parser to get data from JSON
        data = p_parser.parse_args()
        pref = data['preference']
        action = data['preference_action']
        added = str(datetime.utcnow())
        
        #get user identity from JSON web token
        user = get_jwt_identity()

        #Instantiate a Preference from models.PreferenceModel 
        new_pref = PreferenceModel(username = user, preference = pref, added = added)

        #action needs to be defined in the original post call. Add or remove params only. Add adds one. Remove removes all rows matching. 
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
            return {'message': 'action parameter must include either "add" or "remove"'}

#Class to gather all known preferences for a given user.    
class GetUserPreference(Resource):
    @jwt_required
    def get(self):
        username = get_jwt_identity()
        return PreferenceModel.return_user_hx(username)

#POST call with latitude and longitude, returns recommendation based on user session.
class Recommender(Resource): 
    @jwt_required
    def post(self):

        #pull out latitude and longitude from post call
        data = r_parser.parse_args()
        latitude = data['latitude']
        longitude = data['longitude']

        #access user from indexed JSON web token
        username = get_jwt_identity()
        rows = PreferenceModel.return_user_hx(username)

        #user history preferences
        prefs = [row['preference'] for row in rows['message']]
        user_matrix = [pal.palate_constructor(item) for item in prefs]

        #local candidates, check out local.py for more.
        ndb = nutrics_db()
        local_matrix, local_items, keys = ndb.seek_local(latitude,longitude)

        array = []
        counter = 0
        #find best match
        for user_item in user_matrix: 
            matches = [cosine(user_item, local) for local in local_matrix]
            best_match = min(matches)
            index_match = matches.index(best_match)
            name = local_items[index_match]
            key = keys[index_match]
            name, latitude, longitude, rest, desc, price, embed = ndb.return_info(name,key)
            array.append(
                {
                    "item_name": name,
                    "description": desc,
                    "location": [float(latitude),float(longitude)],
                    "restaurant": rest,
                    "price": price,
                    "previous_item": prefs[counter],
                    "embedding":embed
                }
            )
            counter += 1
        #close connection to ndb
        ndb.close_connection()

        return {'data': json.dumps(array)}