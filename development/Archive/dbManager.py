import os
import sys
import re
import sqlite3
import csv
from sqlite3 import Error
import json
import numpy as np

from Palate import Palate
pal = Palate()

'''
Python can only handle a single thread db, so here are all the db manager functions.
'''
class db:

    def __init__(self, db_file):
        #establish connection to database
        self.conn = self.create_connection(db_file)
        #function that checks if the database is populated, repopulates with csv file if not.
        self.initialize_database()
        #assign cursor
        self.cursor = self.conn.cursor()

    #Create connection to database
    def create_connection(self,db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
    
        return conn

    def close_connection(self): 
        try: 
            self.conn.close()
        except Error as e: 
            print(e)
            
    #Make a table in the database
    def create_table(self, create_table_sql):
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
            return True
        except Error as e:
            print(e)
            return False
    
    #Add to durham food table
    def create_row_DURHAM(self, food_info):
        sql = f''' INSERT INTO DURHAM(item_name, latitude, longitude, restaurant_name, item_description, price, embedding)
                VALUES(?,?,?,?,?,?,?) '''

        
        self.cursor.execute(sql, food_info)
        self.conn.commit()
        return self.cursor.lastrowid
    
    #Add a new user
    def create_user(self, user_id, password):
    
        sql = f''' INSERT INTO USERS(user_id, password, joined_date)
                VALUES(?,?,?) '''

        joined_date = 'todays date'
        info = (user_id, password, joined_date)
        self.cursor.execute(sql, info)
        self.conn.commit()
        return self.cursor.lastrowid

    #Add a user preference
    def edit_preference(self, user_id, preference, action):
    
        try:

            if action == 'add':
                sql = f''' INSERT INTO PREFS(user_id, preferences)
                        VALUES(?,?) '''
    
                info = (user_id, preference)
                self.cursor.execute(sql, info)
                self.conn.commit()
                return "Added!"

            if action == 'remove':
                sql = f"DELETE FROM PREFS WHERE preferences = '{preference}' and user_id = '{user_id}';"
                self.cursor.execute(sql)
                self.conn.commit()
                return "Successfully removed."

        except Error as e:
            print(e)

    
    def initialize_database(self):
        #create durham food table with params from csv file below
        durham_food_table = "CREATE TABLE DURHAM (item_name NOT NULL, latitude NOT NULL, longitude NOT NULL, restaurant_name NOT NULL, item_description NOT NULL, price NOT NULL, embedding NOT NULL)"
        condition = self.create_table(durham_food_table)

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
                        self.create_row_DURHAM(row + [jsoned])
                        line_count += 1
                    if line_count % 1000 == 0: 
                        print(line_count, '/4000 items added')

        #create users table
        users_table = "CREATE TABLE USERS (user_id NOT NULL, password NOT NULL, joined_date NOT NULL)"
        self.create_table(users_table)

        #create preferences table
        pref_table = "CREATE TABLE PREFS (user_id NOT NULL, preferences NOT NULL)"
        self.create_table(pref_table)
        print('Database built.')


    def login(self, username, password):
        
        e = self.cursor.execute(f'SELECT password FROM USERS WHERE user_id = "{username}";').fetchone()[0]
        if e == password: 
            return True
        else: 
            return False

    def return_candidates(self, latitude, longitude, verbose = 0):
    #find {limit} items closest to {cur_lat, cur_lng}
        limit = 1000
        cur_lat = latitude
        cur_lng = longitude

        #give option to return candidate names in the area for testing
        if verbose == 1: 
        #only fetching the embeddings for speed. 
            e = self.cursor.execute(f'''
            SELECT rowid, item_name FROM DURHAM ORDER BY (({cur_lat}-latitude)*({cur_lat}-latitude)) + (({cur_lng} - longitude)*({cur_lng} - longitude)) ASC LIMIT {limit};
            ''')
            items = e.fetchall()
            return items

        #But default is only fetching the embeddings for speed. 
        e = self.cursor.execute(f'''
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

        return item_names, numped

    def return_user_prefs(self, username, verbose = 0): 


        history = self.cursor.execute(f'''
                SELECT preferences FROM PREFS WHERE user_id = "{username}";
                ''')

        user_hx = [item[0] for item in history.fetchall()]

        #give the option to fetch full history in english
        if verbose == 1: 
            return user_hx
        
        #default is faster palate arrays
        user_matrix = [pal.palate_constructor(item) for item in user_hx]
        return user_matrix

    def fetch_item(self, row_id):
        

        e = self.cursor.execute(f'''
        SELECT item_name, latitude, longitude, restaurant_name, item_description, price FROM DURHAM WHERE rowid = {row_id};
        ''')
        local_item = e.fetchone()
        return local_item
