'''
This file defines our data models.
Created by Joshua D'Arcy on 4/15/2020.
'''
import env
import os

from run import db
from passlib.hash import pbkdf2_sha256 as sha256
from datetime import datetime
from sqlalchemy import asc, desc
from sqlalchemy import select
from math import radians, cos, sin, asin, sqrt

from itsdangerous import URLSafeTimedSerializer

class UserModel(db.Model):

    #establish table
    __tablename__ = 'users'

    # User information
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(120), unique = True, nullable = False)
    username = db.Column(db.String(120), unique = True, nullable = False)
    password = db.Column(db.String(120), nullable = False)

    age = db.Column(db.Integer, nullable = False)
    activity_level = db.Column(db.Integer, nullable = False)
    gender_identity = db.Column(db.Integer, nullable = False)

    admin = db.Column(db.Boolean, nullable = False)
    registered_on = db.Column(db.DateTime, nullable = False)

    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    
    #save user to database
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    #lookup user
    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username = username).first()
    
    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email = email).first()

    #hash password 
    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)
    
    #verify hashed password
    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

    #method to add admin privelages to a user
    @classmethod
    def make_admin(cls,username):
        new_admin = cls.query.filter_by(username=username).first()
        new_admin.admin = True
        db.session.commit()
        return {'message': 'updated {} to have admin privelages.'.format(username)}

    #method to retrieve all users
    @classmethod
    def return_all_users(cls):
        def jsonit(x):
            return {
                'username': x.username,
                'date_joined': str(x.confirmed_on),
                'admin': x.admin
            }
        return {'users': list(map(lambda x: jsonit(x), UserModel.query.all()))}

    @staticmethod
    def generate_confirmation_token(email):
        serializer = URLSafeTimedSerializer(os.getenv('URL_KEY'))
        return serializer.dumps(email, salt= os.getenv('URL_SALT'))

    @staticmethod
    def confirm_token(token, expiration=3600):
        serializer = URLSafeTimedSerializer(os.getenv('URL_KEY'))
        try:
            email = serializer.loads(
                token,
                salt=os.getenv('SECRET_STRING'),
                max_age=expiration
            )
        except:
            return False
        return email

    #method to delete all users
    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Something went wrong with deleting the users. Please try again.'}

#class for preferences model
class PreferenceModel(db.Model): 
    __tablename__ = 'user_preferences'

    #each row in the table has a username, preference, and ID
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), nullable = False)
    preference = db.Column(db.String(120), nullable = False)
    added = db.Column(db.DateTime, nullable=False)

    #save preference to database
    #todo: add dates for preferences for analysis
    def save_to_db(self):
        try:
            db.session.add(self)
            db.session.commit()
            return {'message': 'Preference successfully added'}, 200
        except: 
            return {'message': 'Something went wrong. Try again.'}, 200
    
    #remove preference from database
    def remove_from_db(self): 
        try:
            db.session.query(PreferenceModel).filter(PreferenceModel.username==self.username).filter(PreferenceModel.preference == self.preference).delete()
            db.session.commit()
            return {'message': 'Preference successfully removed.'}, 200
        except:
            return {'message': 'There was an error with removing the preference. Either it does not exist or there was a string matching issue.'}

    #get list of all preferences from database for a given user (authentication required)
    @classmethod
    def return_user_hx(cls, username): 
        def to_json(x): 
            return {
                'username': x.username,
                'preference': x.preference,
                'added': str(x.added)
            }
        return {'message': list(map(lambda x: to_json(x), PreferenceModel.query.filter_by(username = username).all()))}

    @classmethod
    def data_dump(cls): 
        def to_json(x): 
            return {
                'username': x.username, 
                'preference': x.preference, 
                'timestamp': str(x.added)
            }
        return {'message': list(map(lambda x: to_json(x), PreferenceModel.query.all()))}

#security class to blacklist tokens
class RevokedTokenModel(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key = True)
    jti = db.Column(db.String(120))
    
    def add(self):
        db.session.add(self)
        db.session.commit()
    
    #class method decorator allows for JWT blacklist checking without instantiating class
    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti = jti).first()
        return bool(query)

class FoodModel(db.Model): 
    __tablename__ = 'food_table'
    id = db.Column(db.Integer, primary_key = True)
 
    item_name = db.Column(db.String(120), unique = False, nullable = False)
    latitude = db.Column(db.Float, unique = False, nullable = False)
    longitude = db.Column(db.Float, unique = False, nullable = False)
    restaurant_name = db.Column(db.String(120), unique = False, nullable = False)
    item_description = db.Column(db.String(120), unique = False, nullable = False)
    price = db.Column(db.Float, unique = False, nullable = False)
    embedding = db.Column(db.String(120), unique = False, nullable = False)

    #save user to database
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


    @classmethod
    def find_local(cls, lat1, lon1, desired_dist):
        lat1 = float(lat1)
        lon1 = float(lon1)
        #two steps for now --> Get closest 1000 items and put them in ascending order (distance), then cut off list at distance threshold.
        #mysql supports cos and sin to do haversine formula
        #spatial databases also exist and will be much faster
        #this method works while the area is small and the user base is also small. Will need to optimize when app grows. 
        asc_list = cls.query.order_by(asc((lat1-cls.latitude)*(lat1-cls.latitude) + (lon1 - cls.longitude)*(lon1 - cls.longitude))).limit(2000).all()
        rows = [row for row in asc_list if cls.within_range(lat1, lon1, row, desired_dist)]
          
        return rows

    @classmethod
    def within_range(cls, lat1, lon1, row, desired_dist):
        item_distance = cls.haversine(lat1, lon1, row.latitude, row.longitude)
        if item_distance <= desired_dist:
            return True
        else: 
            return False

    @classmethod
    def haversine(cls, lat1, lon1, lat2, lon2):

      R = 6372000.8 # this is meters

      dLat = radians(lat2 - lat1)
      dLon = radians(lon2 - lon1)
      lat1 = radians(lat1)
      lat2 = radians(lat2)

      a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
      c = 2*asin(sqrt(a))

      return R * c

    @classmethod
    def food_dump(cls):
        def to_json(x): 
            return {
                'item_name' : x.item_name,
                'latitude' : x.latitude,
                'longitude' : x.longitude,
                'restaurant_name' : x.restaurant_name,
                'item_description' : x.item_description,
                'price' : x.price,
                'embedding' : x.embedding
                }
        return {'message': list(map(lambda x: to_json(x), FoodModel.query.all()))}

    @classmethod
    def check_food_exists(cls, item_name, latitude, longitude): 
        if cls.query.filter_by(item_name = item_name, latitude = latitude, longitude = longitude).first(): 
            return True
        else: 
            return False


    @classmethod
    def edit_food(cls, food):
        food_row = cls.query.filter_by(item_name = food.item_name, latitude = food.latitude, longitude = food.longitude).first()
        if food_row:
            food_row.item_name = food.item_name
            food_row.latitude = food.latitude
            food_row.longitude = food.longitude
            food_row.price = food.price
            food_row.item_description = food.item_description
            food_row.restaurant_name = food.restaurant_name
            try:
                db.session.commit()
                return {'message': '{} updated.'.format(food_row.item_name)}
            except: 
                return {'message': 'There was a problem updating {}.'.format(food_row.item_name)}
        else:
            return False

    @classmethod
    def remove_food(cls, food):
        food_row = cls.query.filter_by(item_name = food.item_name, latitude = food.latitude, longitude = food.longitude).first()
        food_row.delete()
        return {'message': '{} at {}, {} successfully deleted.'.format(food.item_name, food.latitude, food.longitude)}