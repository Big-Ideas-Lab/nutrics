from utilities.natural_language import Distance #Distance class is a cosine similarity metric implemented in numpy
from utilities.natural_language import Embed #Embed class palatizes items to give them a 30 dim representation
from utilities.nutrition_scoring import Nutrition_Score #for scoring nutritional content based on user information

from PreferenceModel import PreferenceModel #Need to access user data to make tailored recommendations
from UserModel import UserModel #Need user data for nutrition scoring
from FoodModel import FoodModel #Need to access local data for recommendation candidates

from math import radians, cos, sin, asin, sqrt
import json

class Recommendations:
    @classmethod
    def match(cls,username, lat1, lon1, distance):

        user = UserModel.find_by_username(username) 
        #user history preferences, using set to remove duplicates.
        rows = PreferenceModel.return_user_hx(username)
        prefs = list(set([row['preference'] for row in rows['message']]))
        user_matrix = [Embed.palate(item) for item in prefs]

        #find local candidates
        food_rows = FoodModel.find_local(lat1, lon1, distance)
        local_matrix = [json.loads(food.embedding) for food in food_rows]
        if len(local_matrix) == 0:
            return {'message': 'There are no food items within {} meters of coordinates {}, {}. Please expand your distance parameter.'.format(distance, lat1, lon1)}
        array = []
        counter = 0
        #find best match
        for user_item in user_matrix: 
            matches = [Distance.cosine(user_item, local) for local in local_matrix]
            best_match = min(matches)
            index_match = matches.index(best_match)
            info = food_rows[index_match]
            distance = cls.haversine(lat1, lon1, info.latitude, info.longitude)

            nutrition_object = Nutrition_Score(user.age, user.gender_identity, user.activity_level, info.nutrition)
            recommended_nutrition = json.dumps(nutrition_object.recommended)
            score = nutrition_object.score

            array.append(
                {
                    "item name": info.item_name,
                    "based_on": prefs[counter],
                    "description": info.item_description,
                    "restaurant": info.restaurant_name,
                    "price": info.price,
                    "location": [float(info.latitude),float(info.longitude)],
                    "distance": distance,
                    "match to {} (previous item)".format(prefs[counter]): 1 - best_match, #cosine similarity
                    "nutrition score": score,
                    "recommended nutrition":recommended_nutrition,
                    "actual nutrition":info.nutrition,
                    "embedding": info.embedding
                }
            )
            counter += 1
        return array
    
    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):

      R = 6372000.8 # this is meters

      dLat = radians(lat2 - lat1)
      dLon = radians(lon2 - lon1)
      lat1 = radians(lat1)
      lat2 = radians(lat2)

      a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
      c = 2*asin(sqrt(a))

      return R * c