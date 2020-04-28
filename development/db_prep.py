'''
This is a database conversion helper to structure a SQL database from a local csv file. It has limited error catching.

EXAMPLE USAGE:
>> cd nutrics
>> python db_prep.py food.csv nutrics.db

ASSUMPTIONS: 

1) A .csv file WITH "|" DELIMITER and column headers formatted (in this order): 
item_name | latitude | longitude | restaurant_name | item_description | price

2) The .csv file has been cleaned for formatting errors. There should not be any "|" except for the delimiters.

3) There are not any missing values. An empty string is fine and will not trip up the pipeline. 

4) There is no database with the same name in the same directory. This will cause a non-unique error. In the future,
databases should be updatable via the API. For this MVP, we will do an all-or-nothing approach where the database must be complete
prior to deploying the Docker container.

5) The python file needs to run in the same directory as Palate.py, the csv file, and where you plan to deposity the new db file. 


Created by Joshua D'Arcy on 4.23.2020.
'''

import os
import sys
import re
import sqlite3
import csv
from sqlite3 import Error
import json
import numpy as np

from nlp_resources.utilities import Embed
from nlp_resources.utilities import Distance

class db:

    def __init__(self, db_file_path, csv_file_path):

        self.csv_file_path = csv_file_path
        self.db_file_path = db_file_path
        #establish connection to database
        self.conn = self.create_connection(db_file_path)
        #assign cursor
        self.cursor = self.conn.cursor()
        #function that checks if the database is present / populated, repopulates with csv file if not.
        self.initialize_database()

    #Create connection to database
    def create_connection(self,db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
    
        return conn

    #Close connection to database
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
    def create_row(self, food_info):
        sql = f''' INSERT INTO FOOD_TABLE (item_name, latitude, longitude, restaurant_name, item_description, price, embedding)
                VALUES(?,?,?,?,?,?,?) '''

        
        self.cursor.execute(sql, food_info)
        self.conn.commit()
        return self.cursor.lastrowid

    def initialize_database(self):
        #create durham food table with params from csv file below
        food_table = "CREATE TABLE FOOD_TABLE (item_name NOT NULL, latitude NOT NULL, longitude NOT NULL, restaurant_name NOT NULL, item_description NOT NULL, price NOT NULL, embedding NOT NULL)"
        condition = self.create_table(food_table)

        if condition == False:
            print('\n---*-----*-----\nPRE-EXISTING DATABASE ERROR:\n---*-----*-----')
            print(f'> Something went wrong.\n> Is there already a database with the name "{self.db_file_path}" in your directory?\n> The SQL engine link must be unique. Remove duplicates and continue.')
        
        
        if condition == True:
            print(f'Building database {self.db_file_path}...') 
        #populate food database with contents of csv file. WILL FAIL if there are missing inputs (NOT NULL parameter)
        #csv file uses a | delimiter because some food entries use ','
            with open(self.csv_file_path) as csv_file: 
                csv_reader = csv.reader(csv_file, delimiter='|')
                line_count = 0

                for row in csv_reader:
                    #skip header
                    if line_count == 0:
                        line_count += 1

                    else: 
                        #collect item name
                        item = row[0]

                        #construct palate embedding
                        palate = Embed.palate(item)
                        #SQL doesn't accept arrays so need to serialize into JSON strings
                        jsoned = json.dumps(palate.tolist()) 

                        #add in row to SQL database
                        self.create_row(row + [jsoned])

                        #progress
                        line_count += 1

                    #keep track every 1000 entries
                    if line_count % 1000 == 0: 
                        print(f'{line_count} items from {self.csv_file_path} added.')

            print(f'{self.db_file_path} built from {self.csv_file_path}')

if __name__ == "__main__":

    try:
        csv_name = sys.argv[1]
        db_name = sys.argv[2]
    except:
        print('Command line arguments must be in order >> python db_prep.py [PATH_INPUT_CSV_FILE] [PATH_RETURN_DATABASE_NAME]')
        sys.exit()
      
    if db_name != 'nutrics.db': 
        print("---*-----*-----\nWARNING:\n---*-----*-----")
        print(f">You named your database {db_name}.\n>This file converter will still work, but the FLASK / Docker application looks for something called 'nutrics.db'\n")
    
    with open(csv_name) as f:
        reader = csv.reader(f, delimiter = '|')
        row1 = next(reader)
        #check if comma separated
        if len(row1) < 2:
            print("---*-----*-----\nFORMAT ERROR:\n---*-----*-----\n") 
            print('> Bad delimiter detected. db_prep expects a delimiter of "|".\n> Some food items / descriptions may have commas which will corrupt this process.\n> Please update the csv file to have a "|" delimiter.\n')
            sys.exit()

    #run db class with arguments
    db(db_name, csv_name)
    