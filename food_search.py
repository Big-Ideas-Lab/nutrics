#---------------------------------------------------------------------------------------------
                #PART 0: Imports, NLP database load, nutrition tree build
#---------------------------------------------------------------------------------------------
from bs4 import BeautifulSoup
import os
import requests
import urllib.request as urllib2
import re
import googlemaps as gmap
import json
from geopy.geocoders import Nominatim
import gensim
import pandas as pd
import numpy as np
from scipy import spatial
import sys

sys.setrecursionlimit(3000)

print("Loading NLP Model...")
#---------------------------------------------------------------------------------------------
#importing the nlp model
nlp_model = gensim.models.KeyedVectors.load_word2vec_format('/Users/christinalle/Desktop/GoogleNews-vectors-negative300.bin.gz', binary = True)
print("NLP Model Loaded")

#function to read nutritional database csv, word2vec for each item, convert vectors to searchable tree
#---------------------------------------------------------------------------------------------
def word2vec_func(string):
    word_array = string.split()
    single_vector = np.zeros(300)
    for word in word_array:
        try:
            single_vector += nlp_model.get_vector(word)
        except:
            continue
    return single_vector

KEY = 'insert_keys'

#---------------------------------------------------------------------------------------------
     #PART 1: Find local restaurants, compare to AllMenus.com, construct food dataset
#---------------------------------------------------------------------------------------------

#setup Google search API, default type = 'restaurant' but can use other queries
#---------------------------------------------------------------------------------------------

class google_api_search(object):

    def search_parse(self, lat, lng):
        location = (lat, lng)
        # Query google places api
        goog = gmap.Client(key=self.api_key)
        geocode_result = goog.places(query=self.query, location=location, radius=self.radius, type = 'restuarant')

        # Collect results
        results = geocode_result['results']

        # Clean JSON and create list
        geo_list = []
        for result in results:
            name = result['name'].lower()
            latitude = result['geometry']['location']['lat']
            longitude = result['geometry']['location']['lng']
            geo_list.append((name, (latitude, longitude)))

        return geo_list

    def __init__(self, query='restaurant', radius=1000):
        # set parameters
        self.radius = radius
        self.api_key = KEY
        self.query = query
        # run search parse and create an instance variable called geo_list that you can reference
        # self.geo_list = self.search_parse(35.9940, -78.8986)

#function to help the "About Grubhub" web scraping issue
#---------------------------------------------------------------------------------------------
def sort_header(bea_soup):
    all_headers = bea_soup.find_all('h1')
    for header in all_headers:
        text = header.get_text()
        if 'Grub' in text:
            continue
        else:
            return text

def collect_rtp(rad,lat,long, city):

    # testing difference radii, questions about how to get more restaurants
    set1 = set(google_api_search(query='restaurant|dining', radius=rad).search_parse(lat, long))
    # if city == "Raleigh":
    #     print(set1)

    # find the union of all the sets (a set will inherently get rid of multiples)
    source_list = set1

    # split the geo_list into two separate arrays, one for purely names and one for locations
    names, locations = zip(*source_list)
    map_locations = dict(zip(names, locations))

    # WEB SCRAPING

    # starting link for allmenus, call BeautifulSoup
    URL_base = "https://www.allmenus.com/nc/" + city + "/-/"
    page = urllib2.urlopen(URL_base)
    soup = BeautifulSoup(page, "html.parser")
    all_possible_links = soup.findAll("a", {"data-masterlist-id": re.compile(r".*")})
    # if city == "Raleigh":
    #     print(all_possible_links)

    # all the correct, cleaned links gotten from BeautifulSoup
    links = []

    # list of restaurant names obtained from the links
    master_list = []

    # FINAL list of restaurants used found based on the intersection of master_list and names from above
    links_used = []
    locations_used = []
    names_used = []

    city_link = "/nc/" + city + "/"
    # used to traverse all the possibilities on allmenus and find out what matches google places results
    for link in all_possible_links:
        if link.has_attr('href'):
            raw_href = link.attrs['href']
            # print(raw_href)
            wanted_href = raw_href.replace(city_link, "")
            # print(wanted_href)
            turn_string = str(wanted_href)
            find = str(re.search("(?<=-).*", turn_string).group())
            find = find.replace('/menu/', '')
            find = find.replace('-', ' ')
            find = find.replace(' s', '\'s')
            master_list.append(find)
            links.append(raw_href)

            if find in names:
                links_used.append(wanted_href)
                locations_used.append(map_locations.get(find))
                names_used.append(find)

    # find the intersection of the lists
    master_list_set = set(master_list)
    final_list = master_list_set.intersection(names)
    # if city == "Raleigh":
    #     print(links_used)

    URL_base2 = "https://www.allmenus.com/"

    if city == "chapel-hill":
        URL_base2 = "https://www.allmenus.com/nc/chapel-hill/"

    # where all the data is stored for the JSON
    restaurants = []

    for id, location_goog in zip(links_used, locations_used):
        URL = URL_base2 + id
        r = requests.get(URL)
        bsObj = BeautifulSoup(r.content, 'html.parser')

        #Function to parse out any mention of Grubhub
        restaurant = sort_header(bsObj)

        #Check for chains, skip if chain present
        if any (restp['Name'] == restaurant for restp in restaurants):
            continue

        location = location_goog
        name = restaurant
        titles = bsObj.find_all("span", attrs={'class': 'item-title'})
        ingredients = bsObj.find_all("p", attrs={'class': 'description'})

        prices = bsObj.find_all("span", attrs={'class': 'item-price'})


        # where all the menu items are held with the format above
        # use regex to clean up the ingredients, will have to continue adding to this dictionary

        remove = {',': '', '.': '', ':':''}
        pattern = '|'.join(sorted(re.escape(k) for k in remove))

        #cleaning/processing of ingredients by menu item
        #create array of menu items

        menu = []
        for item, price, ingredient in zip(titles, prices, ingredients):

            menu_item = {
            "item": "",
            "price": "",
            "ingredients": []
            }

            #menu name
            menu_item["item"] = item.get_text()

            #menu price
            stripped_price = price.get_text()
            stripped_price = stripped_price.strip(' \t\n')
            menu_item["price"] = stripped_price
            clean_ingredient = str(ingredient.get_text())


            clean_ingredient = re.sub(pattern, lambda m: remove.get(m.group(0).upper()), clean_ingredient, flags=re.IGNORECASE)
            current_ingredient = re.split("[\s,\&]", clean_ingredient)

            if len(current_ingredient) == 1:
                current_ingredient = re.split("[\s,\&]", menu_item["item"])

            final_ingredient = []

            #NLP to find food
            for word in current_ingredient:
                try:
                    if nlp_model.similarity('edible', word) > .1 and nlp_model.similarity('food', word) > .15:
                        final_ingredient.append(word)
                except:
                    continue

            menu_item['ingredients'] = final_ingredient

            menu.append(menu_item)

        data = {
            "Name": name,
            "Location": location,
            "Menu": menu
        }
        restaurants.append(data)

        # if city == 'chapel-hill':
        #     print(restaurants)

    return restaurants

def run_rtp():
    cities = ['Apex', 'Cary', 'chapel-hill', 'Durham', 'Morrisville', 'Raleigh']
    geolocations = [(35.73227,-78.8503), (35.7915, -78.7811), (35.9132, -79.0558), (35.9940, -78.8986), (35.8235, -78.8256), (35.7796, -78.6382)]
    final_dict = {}
    for city, geolocation in zip(cities, geolocations):
        temp = collect_rtp(500, geolocation[0], geolocation[1], city)
        file_name = city + '.json'
        if city == 'chapel-hill':
            city = 'Chapel Hill'
            with open(file_name, 'w') as json_file:
                json.dump(temp, json_file)
        final_dict[city] = temp
        # print(final_dict)
        print(city + ' is done')

    # print(final_dict)
    with open('rtp.json', 'w') as json_file:
        json.dump(final_dict, json_file)


if __name__ == "__main__":
    run_rtp()