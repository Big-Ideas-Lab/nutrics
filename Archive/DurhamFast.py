import pickle
from math import radians, cos, sin, asin, sqrt

menu_path = 'open_menu_Durham4km.pickle'

#Outside of function. You can replace this with a SQL database connection later

with open(menu_path, 'rb') as handle: 
    data = pickle.load(handle)

class GeoLocalFast(): 

    def __init__(self,lat,lon, distance): 
        #Assign parameters
        self.lat = lat
        self.lon = lon
        self.distance = distance

        self.candidates = self.get_nearby()

    def get_nearby(self): 
        
        #Construct geo_array
        geo_array = [(float(data[rest]['latitude']), float(data[rest]['longitude'])) for rest in data]

        #Find distance between user and item
        distances = list(map(lambda x: self.haversine(self.lon, self.lat, x[1], x[0]),geo_array))

        #Filter for items within range
        within_range = [idx for idx, element in enumerate(distances) if element < self.distance]

        #Re-index candidate names with option keys
        candidates = list(map(lambda x: list(data.keys())[x], within_range))

        #Filter original dict
        candidate_dictionary = {candidate_key: data[candidate_key] for candidate_key in candidates}
        
        return candidate_dictionary


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