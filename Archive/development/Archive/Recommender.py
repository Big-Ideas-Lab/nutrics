from scipy.spatial.distance import cosine
from numpy import mean
from Palate import Palate
from GeoLocal import LocalFinder
from DurhamFast import GeoLocalFast
import json
from math import radians, cos, sin, asin, sqrt
import datetime

'''
This module is designed to be a simple implementation of our recommendation model, based on cosine distances.
Created by Joshua D'Arcy, Sabrina Qi, and Aman Ibrahim on 2/27/2020
'''

class Recommend: 

    def __init__(self, user_hx_arg, latitude, longitude, distance):

        ts1 = datetime.datetime.now().timestamp()
        self.user_hx = user_hx_arg
        self.latitude = latitude
        self.longitude = longitude
        self.distance = distance
        self.rec_dict = {}

        ts2 = datetime.datetime.now().timestamp()
        print("Time to init: " + str(ts2 - ts1) + "seconds")

        self.seek_local()
        ts3 = datetime.datetime.now().timestamp()
        print("Time to find local items: " + str(ts3 - ts2) + "seconds")

        self.palatize()
        ts4 = datetime.datetime.now().timestamp()
        print("Time to palatize / dim reduction: " + str(ts4 - ts3) + "seconds")

        self.ranking()
        ts5 = datetime.datetime.now().timestamp()
        print("Time to compare local items: " + str(ts5 - ts4) + "seconds")

    #Use LocalFinder to find local candidates
    def seek_local(self):
        # self.local_candidates = LocalFinder(self.latitude, self.longitude, self.distance).candidates
        self.local_candidates = GeoLocalFast(self.latitude, self.longitude, self.distance).candidates

        self.local_items = list(self.local_candidates.keys())
    
    #Use Palate to convert local candidates / user history to palate vectors
    def palatize(self): 
        pal = Palate()
        self.local_matrix = [pal.palate_constructor(local) for local in self.local_items]
        self.user_matrix = [pal.palate_constructor(usx) for usx in self.user_hx]

    #Compare local candidates to user history and find best matches
    def ranking(self):
        i=0
        for user_item in self.user_matrix: 
            matches = [cosine(user_item, local_item) for local_item in self.local_matrix]

            
            best_match = min(matches)
            self.rec_dict[f'rec_{i}'] = {}


            index_match = matches.index(best_match)

            #give a percent match (not really a percent but still)
            percent = int(round((1-best_match)**8,2) * 100)

            name = self.local_items[index_match]

            self.rec_dict[f'rec_{i}']['item'] = name
            self.rec_dict[f'rec_{i}']['percent_match'] = percent
            self.rec_dict[f'rec_{i}']['restaurant'] = self.local_candidates[name]['restaurant']
            self.rec_dict[f'rec_{i}']['price'] = self.local_candidates[name]['price']
            self.rec_dict[f'rec_{i}']['distance'] = round(self.haversine(self.latitude, self.longitude, float(self.local_candidates[name]['latitude']), float(self.local_candidates[name]['longitude'])), 2)
            self.rec_dict[f'rec_{i}']['description'] = self.local_candidates[name]['description']
            self.rec_dict[f'rec_{i}']['previous_match'] = self.user_hx[i]


            # print(f'Because you liked {self.user_hx[i]}, you may also like {name} at {restaurant} ({percent}% match, only {distance}m away)')

            i+=1

    def haversine(self,lon1, lat1, lon2, lat2):

        # convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        r = 6371 # Radius of earth in kilometers. Use 3956 for miles
        return c * r



    