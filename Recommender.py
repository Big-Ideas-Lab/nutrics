from scipy.spatial.distance import cosine
from numpy import mean
from Palate import Palate
from GeoLocal import LocalFinder
import json
import math
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
        print("time to init: " + str(ts2 - ts1) + "seconds")

        self.seek_local()
        ts3 = datetime.datetime.now().timestamp()
        print("time to local: " + str(ts3 - ts2) + "seconds")

        self.palatize()
        ts4 = datetime.datetime.now().timestamp()
        print("time to palatize: " + str(ts4 - ts3) + "seconds")

        self.ranking()
        ts5 = datetime.datetime.now().timestamp()
        print("time to rank: " + str(ts5 - ts4) + "seconds")

    #Use LocalFinder to find local candidates
    def seek_local(self):
        self.local_candidates = LocalFinder(self.latitude, self.longitude, self.distance).candidates
        self.local_items = list(self.local_candidates.keys())
    
    #Use Palate to convert local candidates / user history to palate vectors
    def palatize(self): 
        pal = Palate()
        self.local_matrix = [pal.palate_constructor(local) for local in self.local_items]
        self.user_matrix = [pal.palate_constructor(usx) for usx in self.user_hx]

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
            self.rec_dict[f'rec_{i}']['distance'] = round(self.find_distance(self.local_candidates[name]['latitude'], self.local_candidates[name]['longitude']), 2)
            self.rec_dict[f'rec_{i}']['previous_match'] = self.user_hx[i]


            # print(f'Because you liked {self.user_hx[i]}, you may also like {name} at {restaurant} ({percent}% match, only {distance}m away)')

            i+=1

    def find_distance(self, lat2, lon2): 

        #radius of earth
        R = 6373.0

        #lat1 / lat2
        lat1 = math.radians(self.latitude)
        lon1 = math.radians(self.longitude)

        #find deltas
        dlon = lon2 - lon1
        dlat = lat2 - lat1

        #Haversine formula 
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c

        return distance




    