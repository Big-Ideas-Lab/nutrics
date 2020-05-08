# '''
# This file defines the resources used by the Flask application.
# Created by Joshua D'Arcy on 4/15/2020.
# '''


# #flask imports
# from flask_restful import Resource
# from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_current_user)
# from flask_mail import Message 
# from flask import url_for

# #local imports
# from models import UserModel, RevokedTokenModel, PreferenceModel, FoodModel
# from request_parsers import u_parser, p_parser, a_parser, r_parser, e_parser, f_parser, fe_parser
# from local import nutrics_db
# from nlp_resources.utilities import Distance
# from nlp_resources.utilities import Embed
# from Recommender import Recommendations
# from run import app, mail

# #general python helpers
# from datetime import datetime
# # from itsdangerous import URLSafeTimedSerializer
# import json


# #Register users
# class UserRegistration(Resource):
#     def post(self):
#         data = u_parser.parse_args()
        
#         if UserModel.find_by_username(data['username']):
#             return {'message': 'Username "{}" is already taken. Please choose another username.'.format(data['username'])}
        
#         if UserModel.find_by_email(data['email']):
#             return {'message': 'Email address "{}" is already taken. Please enter a different email address.'.format(data['email'])}

#         new_user = UserModel(
#             username = data['username'],
#             password = UserModel.generate_hash(data['password']),
#             email = data['email'],
#             age = data['age'], 
#             gender_identity = data['gender_identity'],
#             activity_level = data['activity_level'],
#             admin = False,
#             registered_on = datetime.now(), 
#             confirmed = False, 
#             confirmed_on = None
#         )
        
#         #for better security, can limit refresh delta for refresh token. Or get rid of refresh priveleges altogether.
#         # try:
#         new_user.save_to_db()
#         registration_token = UserModel.generate_confirmation_token(new_user.email)
#         clickable = url_for('emailverification', token = registration_token, _external = True)

#         msg = Message(
#             subject='Verification link for nutrics',
#             recipients=[new_user.email],
#             body=clickable,
#             sender=app.config['MAIL_DEFAULT_SENDER']
#             )
#         mail.send(msg)

#         try:
#             return {
#                 'message': 'User {} was created. Validation link sent to email.'.format(new_user.username),
#                 'email_sent_to': new_user.email
#                 }
#         except:
#             return {'message': 'Something went wrong with user registration.'}, 500

# class EmailVerification(Resource):
#     def get(self): 
#         data = e_parser.parse_args()
#         token = data['token']
#         try: 
#             email = UserModel.confirm_token(token)
#         except:
#             return {'message': 'Token is invalid or expired.'}

#         user = UserModel.find_by_email(email)
#         if user.confirmed:
#             return {'message': 'User has already been confirmed. Please login.'}
        
#         else: 
#             user.confirmed = True
#             user.confirmed_on = datetime.now()
#             user.save_to_db()
#             return {'message':'Congrats! You can now log in.'}

# #todo: Need to build a method to reset / change password. Will require Flask - security (and an email?)
# #Login users and start session with access / refresh keys. Draws from models.UserModel
# class UserLogin(Resource):
#     def post(self):
#         data = u_parser.parse_args()
#         current_user = UserModel.find_by_username(data['username'])

#         if not current_user:
#             return {'message': 'User {} doesn\'t exist. Are you trying to register? Go to the /registration endpoint.'.format(data['username'])}
        
#         if not current_user.confirmed:
#             return {'message': 'You need to register your email.'}
            
#         if UserModel.verify_hash(data['password'], current_user.password):
#             access_token = create_access_token(identity = data['username'])
#             refresh_token = create_refresh_token(identity = data['username'])
            
#             if current_user.admin == True:
#                 return {
#                     'message': 'Logged in as {}. (admin)'.format(current_user.username),
#                     'access_token': access_token,
#                     'refresh_token': refresh_token
#                     }
#             else: 
#                 return {
#                     'message': 'Logged in as {} (user)'.format(current_user.username),
#                     'access_token': access_token,
#                     'refresh_token': refresh_token
#                 }
#         else:
#             return {'message': 'Something went wrong. Please check your password.'}

# #Logout users and blacklist tokens. Adds to models.RevokedTokenModel
# class UserLogoutAccess(Resource):
#     @jwt_required
#     def post(self):
#         jti = get_raw_jwt()['jti']
#         try:
#             revoked_token = RevokedTokenModel(jti = jti)
#             revoked_token.add()
#             return {'message': 'Access token has been revoked. You will be unable to use this token in the future.'}
#         except:
#             return {'message': 'Something went wrong with revoking your access token. Please try again.'}, 500

# #Logout user using refresh token. Adds to models.RevokedTokenModel
# class UserLogoutRefresh(Resource):
#     @jwt_refresh_token_required
#     def post(self):
#         jti = get_raw_jwt()['jti']
#         try:
#             revoked_token = RevokedTokenModel(jti = jti)
#             revoked_token.add()
#             return {'message': 'Refresh token has been revoked. You will be unable to use this token in the future.'}
#         except:
#             return {'message': 'Something went wrong with revoking your refresh token. Please try again.'}, 500

# #create a new access token when given non-revoked refresh token by user
# #todo: write function to access how much longer remaining for refresh token life. Default is 1 day.
# class TokenRefresh(Resource):
#     @jwt_refresh_token_required
#     def post(self):
#         current_user = get_jwt_identity()
#         access_token = create_access_token(identity = current_user)
#         return {'access_token': access_token, 
#         'message': 'Your access token was generated by using a refresh token.', 
#         'days_remaining_for_refresh': 1
#         }

# class Admin(Resource):
#     @jwt_required
#     def post(self):
#         #get data from post call
#         data = a_parser.parse_args()
#         action = data['action']
#         if action == 'update_admin':
#             new_admin = data['new_admin']
        
#         if action == 'edit_food':
#             try:
#                 item_name = data['item_name']
#                 latitude = data['latitude']
#                 longitude = data['longitude']
#                 price = data['price']
#                 restaurant_name = data['restaurant_name']
#                 description = data['description']

#             except: 
#                 return {"message": "Please ensure you have parameters for the new item details.", 
#                         "expected_params" : ["item_name", 'latitude', 'longitude', 'price', 'description', 'restaurant_name']}
#         #check user JWT
#         current_user = get_jwt_identity()
#         row = UserModel.find_by_username(current_user)
#         #verify user with JWT is an admin via role column
#         if not row.admin:
#             return {"message": "Forbidden, you do not have admin privelages."}, 403
#         if row.admin:
#             if action == 'get_users':
#                 return UserModel.return_all_users()
#             if action == 'get_preferences':
#                 return PreferenceModel.data_dump()
#             if action == 'update_admin':
#                 return UserModel.make_admin(new_admin)
#             if action == 'get_foods':
#                 return FoodModel.food_dump()


# #Class to edit preferences
# class EditPreference(Resource): 
#     @jwt_required
#     def post(self):

#         #use parser to get data from JSON
#         data = p_parser.parse_args()
#         pref = data['preference']
#         action = data['preference_action']
#         added = datetime.now()
        
#         #get user identity from JSON web token
#         user = get_jwt_identity()

#         #Instantiate a Preference from models.PreferenceModel 
#         new_pref = PreferenceModel(username = user, preference = pref, added = added)

#         #action needs to be defined in the original post call. Add or remove params only. Add adds one. Remove removes all rows matching. 
#         if action == 'add':
#             try:
#                 new_pref.save_to_db()
#                 return {'message': '{} successfully added for {}.'.format(pref, user)}, 200
#             except:
#                 return {'message': 'There was a problem adding to the preferences database.'}, 500
         
#         if action == "remove":
#             try: 
#                 new_pref.remove_from_db()
#                 return {'message': '{} successfully removed from {}.'.format(pref, user)}, 200
#             except:
#                 return {'message': 'There was a problem removing the item from the preferences database.'}, 500

#         else: 
#             return {'message': 'action parameter must include either "add" or "remove"'}

# #Class to gather all known preferences for a given user.    
# class GetUserPreference(Resource):
#     @jwt_required
#     def get(self):
#         username = get_jwt_identity()
#         return PreferenceModel.return_user_hx(username)

# #POST call with latitude and longitude, returns recommendation based on user session.
# class Recommender(Resource): 
#     @jwt_required
#     def post(self):

#         #pull out latitude, longitude, and distance from post call
#         data = r_parser.parse_args()
#         latitude = float(data['latitude'])
#         longitude = float(data['longitude'])
#         distance = float(data['distance'])

#         #access user from indexed JSON web token. Need user information for recommendation model.
#         username = get_jwt_identity()

#         #use Recommender Module
#         recs = Recommendations.match(username, latitude, longitude, distance)

#         #return data
#         return {'data': json.dumps(recs)}


# class FoodAdd(Resource): 
#     @jwt_required
#     def post(self):

#         #get user identity from JSON web token
#         user = get_jwt_identity()    
#         row = UserModel.find_by_username(user)
#         if not row.admin:
#             return {"message": "Forbidden, you do not have admin privelages that are needed to add / remove food items."}, 403

#         data = f_parser.parse_args()

#         new_food = FoodModel(
#             item_name = data['item_name'],
#             latitude = data['latitude'],
#             longitude = data['longitude'],
#             restaurant_name = data['restaurant_name'],
#             item_description = data['item_description'],
#             price = data['price'],
#             embedding = json.dumps(list(Embed.palate(data['item_name'])))
#         )

#         if FoodModel.check_food_exists(new_food.item_name, new_food.latitude, new_food.longitude): 
#             return {"message": "{} @ {},{} already exists. If you want to edit this entry, go to the food_edit endpoint.".format(data['item_name'],data['latitude'], data['longitude'])}

#         else:
#             try:
#                 new_food.save_to_db()
#                 return {"message": "{} @ {},{} added.".format(data['item_name'],data['latitude'], data['longitude'])}
#             except:
#                 return {"message": "{} @ {},{} was not added. Something went wrong, please try again.".format(data['item_name'], data['latitude'], data['longitude'])}

# class FoodEdit(Resource):
#     @jwt_required
#     def post(self):

#         #get user identity from JSON web token
#         user = get_jwt_identity()    
#         row = UserModel.find_by_username(user)
#         if not row.admin:
#             return {"message": "Forbidden, you do not have admin privelages that are needed to edit / remove food items."}, 403

#         data = fe_parser.parse_args()

#         action = data['action']

#         food = FoodModel(
#         item_name = data['item_name'],
#         latitude = data['latitude'],
#         longitude = data['longitude'],
#         restaurant_name = data['restaurant_name'],
#         item_description = data['item_description'],
#         price = data['price'],
#         embedding = json.dumps(list(Embed.palate(data['item_name'])))
#         )

#         if not FoodModel.check_food_exists(food.item_name, food.latitude, food.longitude):
#             return {'message': '{} at {}, {} does not exist in our database. If you want to add this item, food to /food/add'.format(data['item_name'], data['latitude'], data['longitude'])}

#         if action == 'del':
#             return FoodModel.remove_food(food)
        
#         if action == 'edit':
#             return FoodModel.edit_food(food)

