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
        distance = 1 - np.dot(vA, vB) / (np.linalg.norm(vA) * np.linalg.norm(vB))
        return distance

class Embed: 

    with open('nlp_resources/unique_foods.pickle', 'rb') as handle: 
        dictionary = pickle.load(handle)

    with open('nlp_resources/flavors.pickle', 'rb') as handle: 
        flavors = pickle.load(handle)

    @classmethod
    def palate(cls, food_string, return_sum = True):

        #Our dictionary is not exhaustive, and this function will skip over unknown foods / mispellings
        def attempt_cos(single_food, single_flavor):
            try:
                cosine_distance = Distance.cosine(cls.dictionary[single_food], cls.dictionary[single_flavor])
                return 1 - cosine_distance
            except:
                return 0
            
            return cosine_distance

        #Use a list comprehension to convert each food to its palate representation
        def find_flavor_single(food_single, flavor_array): 
            cos_array = [attempt_cos(food_single,flavor) for flavor in flavor_array]
            # dictionary = dict(zip(self.flavors,cos_array))
            return cos_array

        #split each meal into foods
        food_array = food_string.lower().split()

        palate_array = np.array([find_flavor_single(food, cls.flavors) for food in food_array]).reshape(-1, len(cls.flavors))

        sum_palate_array = np.sum(palate_array, axis = 0)
        
        return sum_palate_array