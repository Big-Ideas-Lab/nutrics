'''
This is the main progam that runs our backend API. 
Current endpoints include palate construction and nutrition estimation.
Do NOT use Flask for production server, it can only handle one request at a time.
'''

import pandas as pd
import numpy as np
import pickle
from scipy import spatial
from flask import Flask
import requests
import json

# Import local modules
from Palate import Palate
from Nutrition import Nutrients

# from GeoLocal import Nearby
# from Recommender import Recommender

#Initialize application
app = Flask(__name__)

#Initialize palate and nutrition modules. 
#Recommender model is not a general init, so have to initialize that one separately.
pal = Palate()
nuts = Nutrients()


#Interface for nutrition estimation model
@app.route('/get_nutrients/<string>')
def return_nutrients(string):
    #Nutrients module has a method called "fast filter" that seeks nutrition value from database
    return nuts.fast_filter(string)

#Interface for palate module

@app.route('/get_palate/<string>')
def return_palate(string):
    #Palate module has a method called "palette_constructor that decomposes foods into their palate signatures"
    return pal.palette_constructor(string)

#Interface for recommendation model

# @app.route('get_recommendation/<json>')
# def return_recommendation(json):
#     candidates = Nearby(json['lat'], json['long'])
#     user_history = json['user_history']
#     sorted_recommendations = Recommender(candidates, user_history)
#     return sorted_recommendations

if __name__ == '__main__':
    #Do not use Flask in deployment. Set debug to False for real testing.
    app.run(host='127.0.0.1', port=8080, debug=True)
