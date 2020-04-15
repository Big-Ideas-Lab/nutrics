#import database class, check to see if database exists. Try building if not. 
from dbManager import db

dbi = db('nutrics.db')
dbi.close_connection()


from flask import Flask
from flask import request
import requests
import json
from SimpleRecommender import Recommender

#Initialize application
app = Flask(__name__)

@app.route('/edit_preference', methods = ['POST'])
def add_preference():

    json_file = request.json
    username = json_file['username']
    preference = json_file['preference']
    action = json_file['action']

    #make connection
    dbi = db('nutrics.db')

    #add or delete preference
    dbi.edit_preference(username,preference, action)

    #close connection
    dbi.close_connection()

    return f"Success: {action} {preference} for {username}."

#Interface for nutrition estimation model
@app.route('/recommendation', methods=['POST'])
def return_recommendation():
    json_file = request.json
    uname = json_file['username']
    ulat = json_file["latitude"]
    ulon = json_file["longitude"]

    #make connection
    dbi = db('nutrics.db')
    #collect user preferences
    user_hx = dbi.return_user_prefs(username= uname, verbose=1)
    #collect user embedded preferences
    user_matrix = dbi.return_user_prefs(username= uname)
    #collect candidates for local area
    item_names, item_matrix = dbi.return_candidates(latitude = ulat, longitude = ulon)
    #close database connection
    dbi.close_connection()

    json_string = Recommender('nutrics.db', user_matrix, user_hx, item_matrix, item_names).options


    #close connection
    dbi.close_connection()
    return json_string


if __name__ == '__main__':
    #Do not use Flask in deployment. Set debug to False for real testing.
    app.run(host='127.0.0.1', port=8080, debug=True)