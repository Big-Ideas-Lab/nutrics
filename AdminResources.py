#flask imports
from flask_restful import Resource
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_current_user)
from flask_mail import Message 
from flask import url_for

#local imports
from UserModel import UserModel
from RevokedTokenModel import RevokedTokenModel
from PreferenceModel import PreferenceModel
from FoodModel import FoodModel
from utilities.request_parsers import u_parser, p_parser, a_parser, r_parser, e_parser, f_parser #abstracted out parser logic to different file
from utilities.natural_language import Distance #Distance class is a cosine similarity metric implemented in numpy
from utilities.natural_language import Embed #Embed class palatizes items to give them a 30 dim representation
from Recommender import Recommendations
from run import app, mail

#general python helpers
from datetime import datetime
import json

def check_admin(): #abstract out this method, since it will be used a lot in this resources file
    current_user = get_jwt_identity() #get current user identity
    row = UserModel.find_by_username(current_user) #find user information in database
    return row.admin #verify user with JWT is an admin via role column. row.admin column is Boolean.

#method to return all user information in database. Defined in models.py.
class AdminUserInfo(Resource):
    @jwt_required
    def post(self):
        if check_admin():
            return UserModel.return_all_users()
        else:
            return {'message': 'You do not have admin privelages.'}, 403

#method to get all user preferences with timestamps in database. Defined in models.py.
class AdminUserPreferences(Resource):
    @jwt_required
    def post(self):
        if check_admin():
            return PreferenceModel.data_dump()
        else: 
            return {'message': 'You do not have admin privelages.'}, 403

#method to change admin role in database. Defined in models.py.
class AdminAccess(Resource):
    @jwt_required
    def post(self):
        if check_admin():
            data = a_parser.parse_args()
            new_admin = data['new_admin']
            return UserModel.make_admin(new_admin)
        else: 
            return {'message': 'You do not have admin privelages.'}, 403

#method to get all food items in database. Defined in models.py.
class AdminFoodDump(Resource):
    @jwt_required
    def post(self):
        if check_admin():
            return FoodModel.food_dump()
        else: 
            return {'message': 'You do not have admin privelages.'}, 403

#method to add new foods to the database. 
class AdminFoodAdd(Resource):
    @jwt_required
    def post(self):
        if check_admin():
            data = f_parser.parse_args()

            #create new FoodModel object
            new_food = FoodModel(
                item_name = data['item_name'],
                latitude = data['latitude'],
                longitude = data['longitude'],
                restaurant_name = data['restaurant_name'],
                item_description = data['item_description'],
                price = data['price'],
                nutrition = data['nutrition'],
                embedding = json.dumps(list(Embed.palate(data['item_name'])))
            ) 

            if FoodModel.check_food_exists(new_food.item_name, new_food.latitude, new_food.longitude): #check to see if it already exists
                return {"message": "{} @ {},{} already exists. If you want to edit this entry, go to the food_edit endpoint.".format(data['item_name'],data['latitude'], data['longitude'])}
            else:
                try:
                    new_food.save_to_db() #if it's a new item, add it.
                    return {"message": "{} @ {},{} added.".format(data['item_name'],data['latitude'], data['longitude'])}
                except:
                    return {"message": "{} @ {},{} was not added. Something went wrong, please try again.".format(data['item_name'], data['latitude'], data['longitude'])}
        else:
            return {'message': 'You do not have admin privelages.'}, 403

#method to edit existing food items. Creates full new Food object and updates columns.
class AdminFoodEdit(Resource):
    @jwt_required
    def post(self):

        if check_admin():
            data = f_parser.parse_args()

            #create a food object with the same item_name, latitude, and longitude as an existing database entry.
            food = FoodModel(
            item_name = data['item_name'],
            latitude = data['latitude'],
            longitude = data['longitude'],
            restaurant_name = data['restaurant_name'],
            item_description = data['item_description'],
            price = data['price'],
            nutrition = data['nutrition'],
            embedding = json.dumps(list(Embed.palate(data['item_name'])))
            )

            
            if not FoodModel.check_food_exists(food.item_name, food.latitude, food.longitude):
                return {'message': '{} at {}, {} does not exist in our database. If you want to add this item, post to admin/food/add'.format(data['item_name'], data['latitude'], data['longitude'])}

            return FoodModel.edit_food(food) #update it the food in the database using the above food object
        else:
            return {'message': 'You do not have admin privelages.'}, 403

#method to remove an existing food item.
class AdminFoodRemove(Resource):
    @jwt_required
    def post(self):
        if check_admin():
            data = f_parser.parse_args()

            food = FoodModel(
            item_name = data['item_name'],
            latitude = data['latitude'],
            longitude = data['longitude']
            )

            #check that the food exists in the database (at that location)
            if not FoodModel.check_food_exists(food.item_name, food.latitude, food.longitude):
                return {'message': '{} at {}, {} does not exist in our database. If you want to add this item, post to admin/food/add'.format(data['item_name'], data['latitude'], data['longitude'])}

            return FoodModel.remove_food(food) #remove that food row from the database
        else:
            return {'message': 'You do not have admin privelages.'}, 403