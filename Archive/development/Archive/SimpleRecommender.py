from scipy.spatial.distance import cosine
from dbManager import db
import json

class Recommender:

    def __init__(self, database, user_matrix, user_hx, item_matrix, item_names): 
        #connect to database
        self.dbi = db(database)
        self.options = self.matcher(user_matrix, user_hx, item_matrix, item_names)


    def matcher(self, user_matrix, user_hx, item_matrix, item_names):

        #simple recommendation model based on cosine distances and best matches
        recs = {}
        counter = 0
        for hx_item in user_matrix:
            recs[f'rec_{counter}'] = {}
            matches = [cosine(hx_item, local_item) for local_item in item_matrix]
            best_match = min(matches)
            index = matches.index(best_match)

            local_item = self.dbi.fetch_item(row_id = item_names[index])
            recs[f'rec_{counter}']['item'] = local_item[0]
            recs[f'rec_{counter}']['latitude'] = local_item[1]
            recs[f'rec_{counter}']['longitude'] = local_item[2]
            recs[f'rec_{counter}']['restaurant'] = local_item[3]
            recs[f'rec_{counter}']['previous_item'] = user_hx[counter]
            counter += 1

        #close database (sqlite3 can only handle single thread, so close connections when no longer needed)
        self.dbi.close_connection()

        #convert to json for return in Flask app
        json_string = json.dumps(recs)

        return json_string

    