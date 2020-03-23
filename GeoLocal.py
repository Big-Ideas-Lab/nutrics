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

    def __init__(self, lat, lon, distance):
        self.lat = lat
        self.lon = lon
        self.distance = distance

        self.headers = {'x-rapidapi-host': os.environ["XYZ-APP-ID"],'x-rapidapi-key': os.environ["XYZ-APP-KEY"]}

        self.ids = self.get_restaurants()

        self.candidates = self.get_menus()


    def get_restaurants(self):
        url = "https://us-restaurant-menus.p.rapidapi.com/restaurants/search/geo"
        querystring = {"page":"1","lon":self.lon,"lat":self.lat,"distance":self.distance}
        response = requests.request("GET", url, headers=self.headers, params=querystring)
        r_data = json.loads(response.content.decode('utf-8'))

        ids = [data['restaurant_id'] for data in r_data['result']['data']] 

        return ids

    def get_menus(self):

        menu_dict = {}
        for id in self.ids:  
            url = f"https://us-restaurant-menus.p.rapidapi.com/restaurant/{id}/menuitems"
            querystring = {"page":"1"}
            response = requests.request("GET", url, headers=self.headers, params=querystring)
            r_data = json.loads(response.content.decode('utf-8'))

            for m_item in r_data['result']['data']:

                item = m_item['menu_item_name']
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
                    menu_dict[item]['restaurant'] = m_item['restaurant_name']
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