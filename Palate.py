'''
This module is intended to break down foods into their palate signatures. 
This will result in a lower dimensional space that is 
a) easier to search and 
b) contains only information we care about

Created by Joshua D'Arcy on 2/27/2020.
'''

import pandas as pd
import numpy as np
import pickle
from scipy import spatial
import requests
import json


# Unique foods is a python dictionary (in pickle format) that contains 300dim word embeddings (values) for many foods (keys)
uniq_foods = 'unique_foods.pickle'

# Flavors is a list of flavors that we use to deconstruct each meal into a flavor signature
flavors = 'flavors.pickle'

class Palate:

    #Initialize
    def __init__(self): 
        with open(uniq_foods, 'rb') as handle: 
            self.dictionary = pickle.load(handle)

        with open(flavors, 'rb') as handle: 
            self.flavors = pickle.load(handle)


    def palette_constructor(self,food_string):

        #Our dictionary is not exhaustive, and this function will skip over unknown foods / mispellings
        def attempt_cos(single_food, single_flavor):
            try:
                cosine_distance = 1-spatial.distance.cosine(self.dictionary[single_food], self.dictionary[single_flavor])
                return cosine_distance
            except:
                return 0
            
            return cosine_distance

        #Use a list comprehension to convert each food to its palate representation
        def find_flavor_single(food_single, flavor_array): 
            cos_array = [attempt_cos(food_single,flavor) for flavor in flavor_array]
            dictionary = dict(zip(self.flavors,cos_array))
            return dictionary

        #split each meal into foods
        food_array = food_string.split()

        #construct each food into a palate, then combine all food entries into a JSON for the API
        palate_array = json.dumps([find_flavor_single(food, self.flavors) for food in food_array])

        return palate_array