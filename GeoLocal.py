'''
This module is designed to search for nearby food items. It is called by the recommendation model.
Right now, we will be using a free tier API for proof of concept.

**** !! Needs to be worked on this week.

Created by Joshua D'Arcy on 2/27/2020
'''

import requests
import json
import os

from Palate import Palate

HEADERS = {'x-app-id': os.environ['NX-APP-ID'],'x-app-key': os.environ['NX-APP-KEY'],'Content-Type': "application/json"}

class Location:

    def __init__(self, lat, lng, distance):
        self.lat = lat
        self.lng = lng
        self.distance = distance
        self.pal = Palate()

    # def get_restaurants(self):
    #     url = f"https://trackapi.nutritionix.com/v2/locations?ll={self.lat},{self.lng}&distance={self.distance}"
    #     response = requests.get(url, headers=HEADERS)
    #     data = json.loads(response.content.decode('utf-8'))
    #     nearby_restaurants = [restaurant_ID['brand_id'] for restaurant_ID in data['locations']]
    #     return nearby_restaurants

    # #for simplicity, just returning menu of one of the nearest restaurants
    # def get_menu(self):
    #     nearby = '513fbc1283aa2dc80c000002'
    #     baseurl = f"https://trackapi.nutritionix.com/v2/search/instant?query=food&brand_ids={nearby}&branded_type=1"
    #     response = requests.get(baseurl, headers=HEADERS)
    #     data = json.loads(response.content.decode('utf-8'))

    def return_dummy(self):
        dummy1 = list(json.loads(self.pal.palette_constructor('cheeseburger with fries'))[0].values())
        dummy2 = list(json.loads(self.pal.palette_constructor('kale salad'))[0].values())
        dummy3 = list(json.loads(self.pal.palette_constructor('strawberry smoothie'))[0].values())

        return [dummy1,dummy2,dummy3]
