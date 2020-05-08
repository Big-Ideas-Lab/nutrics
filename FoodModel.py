'''
This file defines our Food Model. It builds and edits our database of local items.
Created by Joshua D'Arcy on 4.10.2020.
'''

from run import db 
from datetime import datetime
from sqlalchemy import asc, desc #for sorting items in database by distance
from sqlalchemy import select #utility function from sqlalchemy
from math import radians, cos, sin, asin, sqrt #for Haversine formula


class FoodModel(db.Model): 
    __tablename__ = 'food'
    id = db.Column(db.Integer, primary_key = True)
 
    item_name = db.Column(db.String(120), unique = False, nullable = False)
    latitude = db.Column(db.Float, unique = False, nullable = False)
    longitude = db.Column(db.Float, unique = False, nullable = False)
    restaurant_name = db.Column(db.String(120), unique = False, nullable = False)
    item_description = db.Column(db.String(120), unique = False, nullable = False)
    price = db.Column(db.Float, unique = False, nullable = False)
    nutrition = db.Column(db.String(120), unique = False, nullable = False) #technically a JSON string but here we are.
    embedding = db.Column(db.String(120), unique = False, nullable = False)

    #save food to database
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    #find items within a given radius (desired_dist from lat1, lat2)
    @classmethod
    def find_local(cls, lat1, lon1, desired_dist):
        lat1 = float(lat1)
        lon1 = float(lon1)
        #two steps for now --> Get closest 2000 items and put them in ascending order (distance), then cut off list at distance threshold.
        #mysql supports cos and sin to do haversine formula, sqlite3 does not.
        #spatial databases also exist and will be much faster.
        #this method works while the area is small and the user base is also small. Will need to optimize when app grows.
       
        #find closest 2000 items       
        asc_list = cls.query.order_by(asc((lat1-cls.latitude)*(lat1-cls.latitude) + (lon1 - cls.longitude)*(lon1 - cls.longitude))).limit(2000).all()
        #cut off items outide of radius
        rows = [row for row in asc_list if cls.within_range(lat1, lon1, row, desired_dist)]
    
        return rows

    #calculate distance between rows in table and current location
    @classmethod
    def within_range(cls, lat1, lon1, row, desired_dist):
        item_distance = cls.haversine(lat1, lon1, row.latitude, row.longitude)
        if item_distance <= desired_dist:
            return True
        else: 
            return False

    #formula to calculate number of meters between coordinates. 
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

    #Admin method to collect all food items in database. Admin access required in AdminResources.py.
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

    #Admin method to check for presence of food item in database. Admin access required in AdminResources.py
    @classmethod
    def check_food_exists(cls, item_name, latitude, longitude): 
        if cls.query.filter_by(item_name = item_name, latitude = latitude, longitude = longitude).first(): 
            return True
        else: 
            return False

    #Admin method to edit food items in database. 
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
            return {'message': '{} at {}, {} not found in database.'.format(food.item_name, food.latitude, food.longitude)}

    #Admin method to remove food items in database.
    @classmethod
    def remove_food(cls, food):
        try:
            db.session.query(FoodModel).filter(FoodModel.item_name==food.item_name).filter(FoodModel.latitude==food.latitude).filter(FoodModel.longitude==food.longitude).delete()
            db.session.commit()
            return {'message': '{} at {}, {} successfully deleted.'.format(food.item_name, food.latitude, food.longitude)}, 200
        except:
            return {'message': 'There was an error with removing the fodo item. Either it does not exist or there was a string matching issue.'}
       