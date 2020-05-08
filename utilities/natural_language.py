'''
This module uses natural language processing to generate a "Palate signature" for faster computation.
Created by Joshua D'Arcy on 4/15/2020.
'''

import numpy as np
import pickle
import json


class Distance:
    @staticmethod
    def cosine(vA, vB):
        distance = 1 - np.dot(vA, vB) / (np.linalg.norm(vA) * np.linalg.norm(vB)) # 1 - cosine similarity = cosine distance
        return distance

class Embed: 

    with open('utilities/unique_foods.pickle', 'rb') as handle: 
        dictionary = pickle.load(handle) #unique foods is a python dictionary with 300 dim word embeddings for a few thousand different foods.

    with open('utilities/flavors.pickle', 'rb') as handle: 
        flavors = pickle.load(handle) #flavors is a python list with selected flavors to use with our palate construction method

    @classmethod
    def palate(cls, food_string, return_sum = True):

        #Our dictionary is not exhaustive, and this function will skip over unknown foods / mispellings
        def attempt_cos(single_food, single_flavor):
            try:
                cosine_distance = Distance.cosine(cls.dictionary[single_food], cls.dictionary[single_flavor])
                return 1 - cosine_distance #bring back similarity 
            except:
                return 0
            
            return cosine_distance

        #Use a list comprehension to convert each food to its palate representation
        def find_flavor_single(food_single, flavor_array): 
            cos_array = [attempt_cos(food_single,flavor) for flavor in flavor_array]
            return cos_array

        #split each meal into foods
        food_array = food_string.lower().split()

        palate_array = np.array([find_flavor_single(food, cls.flavors) for food in food_array]).reshape(-1, len(cls.flavors))

        #taking the simple sum for now, can consider average in future or weighted sum/avg.
        sum_palate_array = np.sum(palate_array, axis = 0)
        
        return sum_palate_array