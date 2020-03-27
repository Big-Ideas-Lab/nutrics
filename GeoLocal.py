'''
This module is designed to search for nearby food items. It is called by the recommendation model.
Right now, we will be using a free tier API for proof of concept. 

Created by Joshua D'Arcy on 2/27/2020
'''

import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

class LocalFinder:

    #Inititialize class
    def __init__(self, lat, lon, distance):
        self.lat = lat
        self.lon = lon
        self.distance = distance

        #Pull headers from .env file
        self.headers_V2 = {'x-app-id': os.environ["ID"],'x-app-key': os.environ["KEY"]}
        self.headers_V1 = {'appId': os.environ["ID"],'appKey': os.environ["KEY"]}

        #Collect local restaurants
        self.ids = self.get_restaurants()

        #Collect menu data from local restaurants
        self.candidates = self.get_menus()

    #Collect local restaurant IDs
    def get_restaurants(self):

        PARAMS = {'ll':f'{self.lat},{self.lon}', 'distance':f'{self.distance}'}
        r = requests.get('https://trackapi.nutritionix.com/v2/locations', params=PARAMS,headers=self.headers_V2)
        r_data = r.json()
        ids = [loc['brand_id'] for loc in r_data['locations']]
        return ids

    #Collect menu data from local restaurants, based on restaurant IDs
    def get_menus(self):

        menu_dict = {}
        for id in self.ids:  
            json_post = {
                "appId":os.environ["ID"],
                "appKey":os.environ["KEY"],
                "offset":0, 
                "limit":50,
                "filters":{
                    "brand_id": f"{id}" 
                    }, 
                # "sort":{
                #     "field":"_score",
                #     "order":"desc"
                # }
                }
            r = requests.post('https://api.nutritionix.com/v1_1/search', json=json_post)
            r_data = r.json()
    
            for m_item in r_data['hits']:

                item = m_item['fields']['item_name']
                menu_dict[item] = {}

                try:
                    menu_dict[item]['latitude'] = m_item['geo']['lat']
                except:
                    menu_dict[item]['latitude'] = ''

                try:
                    menu_dict[item]['longitude'] = m_item['geo']['lon']
                except:
                    menu_dict[item]['longitude'] = ''

                try:
                    menu_dict[item]['restaurant'] = m_item['fields']['brand_name']
                except:
                    menu_dict[item]['restaurant'] = ''

                try:
                    menu_dict[item]['description'] = m_item['menu_item_description']
                except:
                    menu_dict[item]['description'] = ''

                try:
                    menu_dict[item]['price'] = m_item['menu_item_pricing'][0]['price']
                except: 
                    menu_dict[item]['price'] = ''

        return menu_dict