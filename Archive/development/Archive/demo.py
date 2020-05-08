import os
import sys
import re
import sqlite3
from sqlite3 import Error

import pickle
import csv
from scipy.spatial.distance import cosine
from Palate import Palate
import json
pal = Palate()


sys.path.append(os.path.realpath("."))
from pprint import pprint
import inquirer

import numpy as np


#Create connection to database
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return conn
 
#Make a table in the database
def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        return True
    except Error as e:
        print(e)
        return False

#Add to durham food table
def create_row_DURHAM(conn, food_info):
 
    sql = f''' INSERT INTO DURHAM(item_name, latitude, longitude, restaurant_name, item_description, price, embedding)
              VALUES(?,?,?,?,?,?,?) '''

    cur = conn.cursor()
    cur.execute(sql, food_info)
    conn.commit()
    return cur.lastrowid

#Add a new user
def create_user(conn, user_id, password):
 
    sql = f''' INSERT INTO USERS(user_id, password, joined_date)
              VALUES(?,?,?) '''

    joined_date = 'todays'
    cur = conn.cursor()
    info = (user_id, password, joined_date)
    cur.execute(sql, info)
    conn.commit()
    return cur.lastrowid

#Add a user preference
def add_preference(conn, user_id, accepted):
 
    sql = f''' INSERT INTO PREFS(user_id, preferences)
              VALUES(?,?) '''

    cur = conn.cursor()
    info = (user_id, accepted)
    cur.execute(sql, info)
    conn.commit()
    return cur.lastrowid

print('Building database... ')
conn = create_connection('nutrics.db')
cursor = conn.cursor()

#create durham food table with params from csv file below
durham_food_table = "CREATE TABLE DURHAM (item_name NOT NULL, latitude NOT NULL, longitude NOT NULL, restaurant_name NOT NULL, item_description NOT NULL, price NOT NULL, embedding NOT NULL)"
condition = create_table(conn, durham_food_table)

if condition == True: 
#populate food database with contents of csv file. WILL FAIL if there are missing inputs (NOT NULL parameter)
#csv file uses a | delimiter because some food entries use ','
    with open('/Users/joshuadarcy/Documents/nutrics/food.csv') as csv_file: 
        csv_reader = csv.reader(csv_file, delimiter='|')
        line_count = 0
        for row in csv_reader: 
            if line_count == 0:

                line_count += 1
            else: 
                item = row[0]
                palate = pal.palate_constructor(item)
                jsoned = json.dumps(palate.tolist()) #SQL doesn't accept arrays so need to serialize into JSON strings
                create_row_DURHAM(conn, row + [jsoned])
                line_count += 1
            if line_count % 1000 == 0: 
                print(line_count, '/4000 items added')

#create users table
users_table = "CREATE TABLE USERS (user_id NOT NULL, password NOT NULL, joined_date NOT NULL)"
create_table(conn,users_table)

#create preferences table
pref_table = "CREATE TABLE PREFS (user_id NOT NULL, preferences NOT NULL)"
create_table(conn, pref_table)

print('Database built.')

def login(username, password):
    e = cursor.execute(f'SELECT password FROM USERS WHERE user_id = "{username}";').fetchone()[0]
    if e == password: 
        return True
    else: 
        return False


authenticated = False
username = ''

class app(): 

    def __init__(self): 
        self.authenticated = False
        self.username = ''

    def router(self, answers):
        if answers['action'] == 'Login': 
            self.username = input('Username: ')
            try:
                password = input('Password: ')
                if login(self.username, password): 
                    print('---------*------------*----------')
                    print('Authentication successful.')
                    print('---------*------------*----------')
                    self.authenticated = True
                else:
                    print('---------*------------*----------')
                    print('Login failed. Check username and password.')
                    print('---------*------------*----------')
                    self.authenticated = False
            except: 
                print('---------*------------*----------')
                print(f"Sorry {self.username}, do you exist? We don't have those login credentials in our database.")
                print('---------*------------*----------')

        if answers['action'] == "Create new user": 
            self.username = input('Enter your new username here: ')
            password = input('Password: ')
            create_user(conn, self.username, password)
            print('---------*------------*----------')
            print(f'Welcome to nutrics, {self.username}!')
            print('---------*------------*----------\n')
            

        if answers['action'] == "Add preference for a user":
            if self.authenticated == True:
                pref = input(f'Hi {self.username}, tell us what you like:')
                add_preference(conn, self.username, pref)
                print('-------------------------------')
                print(f'Preference {pref} added.')
                print('-------------------------------')
            else: 
                print('-------------------------------')
                print("No one is logged in. Please login to continue.")
                print('-------------------------------')

        if answers['action'] == "Logout": 
            self.authenticated = False
            print('-------------------------------')
            print('Logout sucessful.')
            print('-------------------------------')

        if answers['action'] == "Find local items for user": 
            
            if self.authenticated == True:
                #find {limit} items closest to {cur_lat, cur_lng}
                limit = 1000
                cur_lat = 35.880705
                cur_lng = -78.849392
                e = cursor.execute(f'''
                SELECT rowid, embedding FROM DURHAM ORDER BY (({cur_lat}-latitude)*({cur_lat}-latitude)) + (({cur_lng} - longitude)*({cur_lng} - longitude)) ASC LIMIT {limit};
                ''')
                embedded = e.fetchall()

                #parse and reconstruct into a list of the embeddings within a given area
                item_names = []
                vectors = []
                for vector in embedded:
                    item_names.append(vector[0])
                    loaded = json.loads(vector[1])
                    vectors.append(loaded)
    
                #build into numpy array for speed
                numped = np.array(vectors)

                history = cursor.execute(f'''
                SELECT preferences FROM PREFS WHERE user_id = "{self.username}";
                ''')

                user_hx = [item[0] for item in history.fetchall()]
                
                user_matrix = [pal.palate_constructor(item) for item in user_hx]

                counter = 0
                for hx_item in user_matrix:
                    matches = [cosine(hx_item, local_item) for local_item in numped]
                    best_match = min(matches)
                    index = matches.index(best_match)
                    e = cursor.execute(f'''
                    SELECT item_name, latitude, longitude, restaurant_name, item_description, price FROM DURHAM WHERE rowid = {item_names[index]};
                    ''')
                    local_item = e.fetchone()
                    print(f'\nRecommendation based on {user_hx[counter]}:')
                    print('-------------------------------------------------------------------')
                    print(f'    You may also like {local_item[0]} @ {local_item[3]} \n')
                    counter += 1
            else: 
                print('-------------------------------')
                print("You're not authenticated. Please login.")
                print('-------------------------------')

        if answers['action'] == 'Complete session': 
            print('-------------------------------')
            print('Thank you for choosing nutrics.')
            print('-------------------------------')
            return 'quit'


session = app()
questions = [
    inquirer.List(
        "action",
        message="What would you like to do?",
        choices=["Login", "Create new user", "Add preference for a user", "Find local items for user", "Logout", "Complete session"],
    ),
]



while True:
    answers = inquirer.prompt(questions)
    response_code = session.router(answers)
    if response_code == 'quit': 
        break
    