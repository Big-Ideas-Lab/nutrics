'''
This class scores foods based on their nutrition content and user context (age, activity level, and gender identity)
Created by Sabrina Qi with oversight from Duke Nutrition, and later reorganized by Joshua D'Arcy 5.1.2020.
This file needs to be cleaned and optimized prior to production.
'''

import json

class Nutrition_Score: 

    def __init__(self, age, gender_identity, activity, jstring):
        
        self.age = age
        self.gender = gender_identity
        self.activity = activity

        self.recommended = self.recommended_dict()
        self.score = self.nutrientScore(jstring, self.recommended)

    def nutrientScore(self, nutrition_info, recommended_dict_i):
        nutrition_info = json.loads(nutrition_info)
        recDict = recommended_dict_i

        nutrient_fracs={}
        for nutrient in nutrition_info:
            goal = recDict[nutrient]
            actual = nutrition_info[nutrient]
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
        return score

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