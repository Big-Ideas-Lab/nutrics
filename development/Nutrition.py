'''
The Nutrients Class was created to implement our "semantic nutrition model". 
By searching a database created by Duke Nutrition, we can form semantic relationships 
between different foods and estimate their nutritional value based on nearest neighbors

The Nutrition_Score was created to score a food based on it's nutritional content and takes
gender, age, and activity level into account. 

Created by Sabrina Qi and Joshua D'Arcy on 2/27/2020.


**** WARNING ****
This is a deprecated method. Needs plenty of work and was not a priority for the backend.
'''

import pandas as pd
import numpy as np
import pickle
from scipy import spatial
import requests
import json

# Unique foods is a python dictionary (in pickle format) that contains 300dim word embeddings (values) for many foods (keys)
uniq_foods = 'nlp_resources/unique_foods.pickle'

# clean_csv is a nutrition dataset that has been removed of duplicates and pre-processed for text analysis 
clean_csv = 'nlp_resources/clean_foods.csv'

class Nutrients: 

    def __init__(self):

        # Load the unique foods
        with open(uniq_foods, 'rb') as handle: 
            self.dictionary = pickle.load(handle)
        
        # Load the clean nutrition dataset
        self.df = pd.read_csv(clean_csv)

        #Convert each food entry to a 300 dim represenation using word embedding
        vectors = self.df['food_name'].apply(lambda x: self.get_vector_init(x))
        reshaped = np.concatenate(vectors).reshape(-1,300)

        #place in a kd search tree for rapid indexing
        self.tree = spatial.KDTree(reshaped)

    #function to consuct element-wise sum of foods with more than one word (e.g. caesar salad)
    def get_vector_init(self,string):
        base = np.zeros(300) 
        array = string.split()
        for word in array: 
            try: 
                base += self.dictionary[word]
            except:
                continue
        return base

    #needed a different function to make embedding representation for unknown foods
    #this function allows for no matches to occur if word not in our dictionary
    def get_vector_from_array(self, string_array):
        base = np.zeros(300) 

        keeper = []
        for word in string_array: 
            try: 
                base += self.dictionary[word]
            except:
                keeper.append(word)
                continue
        if all(base == np.zeros(300)): 
            print(f'The following words were not in our food dictionary: {keeper}. Please check your spelling, and keep in mind we generally do not use brand names')
            return None

        return base

    def best_NLP_guess(self,string): 
        string_array = string.split()
        try:
            string_array.remove('and')
        except:
            pass

        vector = self.get_vector_from_array(string_array)
        match, row = self.tree.query(vector)
        match = 1 - match

        data = self.df.iloc[row]

        json_data = json.dumps(dict(zip(list(data.keys()[1:]), list(data.values[1:]))))
        return json_data


    #This is filtering search approach that needs to be optimized in the future. 
    #This method will find the longest matching strings that we have in our database
    def fast_filter(self, string): 
        string_array = string.split()

        #'and' is not in our dictionary and is easier to preprocess out.
        try:
            string_array.remove('and')
        except:
            pass

        #initialize filter
        full_filter_size = len(string_array)
        rows = []
        keeper = []

        #funnel approach with reversed range-- biggest filters first.
        for i in reversed(range(full_filter_size)): 

            #start with full filter
            sub_filter = np.array(range(i + 1))
            string = [string_array[index] for index in sub_filter]
            vector = self.get_vector_from_array(string)
            match, row = self.tree.query(vector)
            match = 1 - match

            #if we have a perfect match, append to known match array 'keeper'
            #can set the match to have lower threshold and accept matches like "apple cobbler" for "peach cobbler"
            if match == 1:
                rows.append(self.df.iloc[row])
                keeper.append(string)

            #pass progressively smaller filters looking for matches
            for n in range(full_filter_size - len(sub_filter)):
                sub_filter = sub_filter + np.ones(len(sub_filter))
                string = [string_array[int(index)] for index in sub_filter]
                vector = self.get_vector_from_array(string)
                match, row = self.tree.query(vector)
                match = 1 - match

                if match == 1: 
                    rows.append(self.df.iloc[row])
                    keeper.append(string)
        
        #convert to JSON for API return
        json_strings = json.dumps([dict(zip(list(row.keys()[1:]), list(row.values[1:]))) for row in rows])
        return json_strings

class Nutrition_Score: 

    def __init__(self,age, gender, activity, food):
        
        self.age = age
        self.gender = gender
        self.activity = activity

        self.recommended = self.recommended_dict()
        to_score = Nutrients().fast_filter(food)
        self.score = self.nutrientScore(to_score, self.recommended)

    # #Score menu item
    # #---------------------------------------------------------------------------------------------
    def nutrientScore(self, nutrition_info, recommended_dict_i):
        #convert to json file
        nutrition_info = json.loads(nutrition_info)
    
        recDict = recommended_dict_i


        nutrient_sum_dict={"carbohydrates": 0, "sugar": 0, "total_fats": 0, "sat_fats": 0, "protein": 0, "fiber": 0, "calories": 0, "cholesterol": 0, "potassium": 0, "sodium": 0, "calcium": 0, "magnesium": 0}
        nutrient_fracs={}

        for ingredient in nutrition_info:
            for nutrient in ingredient:
                try: 
                    nutrient_sum_dict[nutrient] = nutrient_sum_dict[nutrient] + ingredient[nutrient] 
                except: 
                    pass

        for nutrient in nutrient_sum_dict:
            goal = recDict[nutrient]
            actual = nutrient_sum_dict[nutrient]
            frac = actual/goal
            nutrient_fracs[nutrient] = frac

        # select weights for each adequacy and moderation for each nutrient
        weight_adequacy, weight_moderation = self.weight(recDict)

        # Scoring
        nutrient_scores_adequacy= {}
        nutrient_scores_moderation = {}
        for nutrient in nutrient_fracs:
            if nutrient_fracs[nutrient] >= 2 :
                nutrient_scores_adequacy[nutrient] = 3* weight_adequacy[nutrient]
                nutrient_scores_moderation[nutrient] = -3* weight_moderation[nutrient]
            if nutrient_fracs[nutrient] >= 1.25 and nutrient_fracs[nutrient] <2:
                nutrient_scores_adequacy[nutrient] = 2* weight_adequacy[nutrient]
                nutrient_scores_moderation[nutrient] = -2* weight_moderation[nutrient]
            if nutrient_fracs[nutrient] >= 1 and nutrient_fracs[nutrient] <1.25:
                nutrient_scores_adequacy[nutrient] = 1* weight_adequacy[nutrient]
                nutrient_scores_moderation[nutrient] = -1* weight_moderation[nutrient]
            if nutrient_fracs[nutrient] >= .75 and nutrient_fracs[nutrient] <1:
                nutrient_scores_adequacy[nutrient] = -1* weight_adequacy[nutrient]
                nutrient_scores_moderation[nutrient] = 1* weight_moderation[nutrient]
            if nutrient_fracs[nutrient] >= .5 and nutrient_fracs[nutrient] <.75:
                nutrient_scores_adequacy[nutrient] = -2* weight_adequacy[nutrient]
                nutrient_scores_moderation[nutrient] = 2* weight_moderation[nutrient]
            if nutrient_fracs[nutrient] >= 0 and nutrient_fracs[nutrient] <.5:
                nutrient_scores_adequacy[nutrient] = -3* weight_adequacy[nutrient]
                nutrient_scores_moderation[nutrient] = 3* weight_moderation[nutrient]
        adequacy = sum(nutrient_scores_adequacy.values())
        moderation = sum(nutrient_scores_moderation.values())
        score = adequacy + moderation # a more positive score is better

        if score <= 0: 
            score = 0
        if score > 0 and score < 30:
            score = score / 30
        if score >= 30: 
            score = 1


        return str(score)

    # Generate the recommended nutritional intake depending on gender and activity
    #---------------------------------------------------------------------------------------------

    def recommended_dict(self):
        gender = self.gender
        age = self.age
        activity = self.activity

        if gender == 0:
            if activity == 0:
                if  age >=16 and age <=18:
                    cals = 2400;percent_totfat = .3;protein = 52;fiber = 30.8
                elif age >=19 and age <=20:
                    cals = 2600;percent_totfat = .27;protein = 56;fiber = 33.6
                elif age >=21 and age <=30:
                    cals = 2400;percent_totfat = .27;protein = 56;fiber = 33.6
                elif  age >=31 and age <=40:
                    cals = 2400;protein = 56;percent_totfat = .27;fiber = 30.8
                elif  age >=41 and age <=50:
                    cals = 2200;percent_totfat = .27;protein = 56;fiber = 30.8
                elif  age >=51 and age <=60:
                    cals = 2200;percent_totfat = .27;protein = 56;fiber = 28
                elif  age >=61:
                    cals = 2000;percent_totfat = .27;protein = 56;fiber = 28
            elif activity == 1:
                if  age >=16 and age <=25:
                    cals = 2800;percent_totfat = .3;protein = 52
                    if age >=16 and age <= 18:
                        fiber = 30.8
                    elif age >=19 and age <= 25:
                        fiber = 33.6
                elif age >=26 and age <=45:
                    cals = 2600;percent_totfat = .27;protein = 56
                    if age >= 26 and age <=30:
                        fiber = 33.6
                    elif age >= 31 and age <= 45:
                        fiber = 30.8
                elif age >=46 and age <= 65:
                    cals = 2400;percent_totfat = .27;protein = 56
                    if age >= 46 and age <= 50:
                        fiber = 30.8
                    elif age >=51:
                        fiber = 28
                elif age >=66:
                    cals = 2200;percent_totfat = .27;protein = 56; fiber=28
            elif activity == 2:
                if  age >=16 and age <=18:
                    cals = 3200;percent_totfat = .3;protein = 52;fiber = 30.8
                elif  age >=19 and age <=35:
                    cals = 3000;percent_totfat = .27;protein = 56
                    if age >= 19 and age <= 30:
                        fiber = 33.6
                    elif age >= 31 and age >= 35:
                        fiber = 30.8
                elif  age >=36 and age <=55:
                    cals = 2800;percent_totfat = .27;protein = 56
                    if age >= 36 and age <= 50:
                        fiber = 30.8
                    elif age >=51 and age <= 55:
                        fiber = 28
                elif  age >=56 and age <=75:
                    cals = 2600;percent_totfat = .27;protein = 56;fiber = 28
                elif age >= 76:
                    cals = 2400;percent_totfat = .27;protein = 56;fiber = 28

            recommended_dict = {'calories':cals/3,'sugar':.09*cals/3,'total_fats': percent_totfat*cals/3,'sat_fats':.06*cals/3,'cholesterol':150/3,'carbohydrates':.55*cals/3,'protein':protein/3,'fiber':fiber/3,'sodium':2300/3,'magnesium':420/3,'potassium':4700/3,'calcium':1250/3} #'totfolate':400/3,'transfat':.01*cals/3,

        elif gender == 1:
            if activity == 0:
                if age >=16 and age <=18:
                    cals = 1800;percent_totfat = .3;fiber = 25.2
                elif  age >=19 and age <=25:
                    cals = 2000;percent_totfat = .27;fiber = 28
                elif  age >=26 and age <=50:
                    cals = 1800;percent_totfat = .27
                    if age >= 26 and age <=30:
                        fiber = 28
                    elif age >30 and age <=50:
                        fiber = 25.2
                elif  age >=51:
                    cals = 1600;percent_totfat = .27;fiber = 22.4
            elif activity == 1:
                if age >=16 and age <=18:
                    cals = 2000;percent_totfat = .3;fiber = 25.2
                elif  age >=19 and age <=25:
                    cals = 2200;percent_totfat = .27;fiber = 28
                elif  age >=26 and age <=50:
                    cals = 2000;percent_totfat = .27
                    if age >= 26 and age <=30:
                        fiber = 28
                    elif age >30 and age <=50:
                        fiber = 25.2
                elif  age >=51:
                    cals = 1800;percent_totfat = .27;fiber = 22.4
            elif activity == 2:
                if age >=16 and age <=30:
                    cals = 2400;percent_totfat = .27
                    if age >=16 and age <=18:
                        fiber = 25.2
                    elif age >18 and age <=25:
                        fiber = 28
                    elif age >= 26 and age <=30:
                        fiber = 28
                elif age >30 and age <=60:
                    cals = 2200;percent_totfat = .27
                    if age >30 and age <=50:
                        fiber = 25.2
                    elif age> 50:
                        fiber = 22.4
                elif age>60:
                    cals = 2000;percent_totfat = .27;fiber = 22.4

            recommended_dict = {'calories':cals/3,'sugar':.09*cals/3,'total_fats': percent_totfat*cals/3,'sat_fats':.06*cals/3,'cholesterol':150/3,'carbohydrates':.55*cals/3,'protein':46/3,'fiber':fiber/3,'sodium':2300/3,'magnesium':320/3,'potassium':4700/3,'calcium':1250/3} #'transfat':.01*cals/3,'totfolate':400/3,'vd':600/3,
        
        else:
            recommended_dict = {'calories':2400/3,'sugar':.09*2400/3,'total_fats': .27*2400/3,'sat_fats':.06*2400/3,'cholesterol':150/3,'carbohydrates':.55*cals/3,'protein':46/3,'fiber':25.2/3,'sodium':2300/3,'magnesium':320/3,'potassium':4700/3,'calcium':1250/3} #'totfolate':400/3,'transfat':.01*2400/3,'vd':600/3,
        
        return recommended_dict


    def weight(self, recDict):
        switcher = {
        'calories': (2,3),
        'sugar': (1,3),
        'total_fats': (1,3),
        'unsatfat': (2,2),
        'sat_fats': (1,3),
        'transfat': (1,3),
        'carbohydrates': (2,3),
        'protein': (2,3),
        'fiber': (3,1),
        'sodium': (1,3),
        'magnesium': (2,1),
        'totfolate': (2,1),
        'potassium': (2,1),
        'vd': (2,1),
        'cholesterol': (1,1), 
        'calcium': (1,1)
        }
        weight_adequacy = {} #{'nutrient': weight_value, etc}
        weight_moderation = {}
        for nutrient in recDict:
            weight_adequacy[nutrient], weight_moderation[nutrient] = switcher[nutrient]
        return weight_adequacy, weight_moderation