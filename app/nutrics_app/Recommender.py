from nlp_resources.utilities import Distance
from nlp_resources.utilities import Embed
from local import nutrics_db
from models import PreferenceModel
from math import sin, cos, sqrt, atan2, radians

class Recommendations:
    @classmethod
    def match(cls,username, lat1, lon1):
        #user history preferences, using set to remove duplicates.
        rows = PreferenceModel.return_user_hx(username)
        prefs = list(set([row['preference'] for row in rows['message']]))
        user_matrix = [Embed.palate(item) for item in prefs]

        #find local candidates
        ndb = nutrics_db()
        local_matrix, local_items, keys = ndb.seek_local(lat1,lon1)

        array = []
        counter = 0
        #find best match
        for user_item in user_matrix: 
            matches = [Distance.cosine(user_item, local) for local in local_matrix]
            best_match = min(matches)
            index_match = matches.index(best_match)
            name = local_items[index_match]
            key = keys[index_match]
            name, lat2, lon2, rest, desc, price, embed = ndb.return_info(name,key)
            distance = cls.find_distance(float(lat1), float(lon1), float(lat2), float(lon2))
            array.append(
                {
                    "item_name": name,
                    "description": desc,
                    "location": [float(lat2),float(lon2)],
                    "distance": distance,
                    "restaurant": rest,
                    "price": price,
                    "previous_item": prefs[counter],
                    "embedding":embed
                }
            )
            counter += 1
        #close connection to ndb
        ndb.close_connection()
        return array
    
    @staticmethod
    def find_distance(lat1, lon1, lat2, lon2): 
        R = 6373.0

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return distance