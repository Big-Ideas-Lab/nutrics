'''
This file is a second database manager for the food database 'nutrics.db'
It is separate from the users database established in models.py. It was separated to more easily allow for updating databases.
Created by Joshua D'Arcy on 4/15/2020.
'''

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy import Table
from sqlalchemy import select
from sqlalchemy import asc
import json
import numpy as np

class nutrics_db:

    def __init__(self): 

        #create engine to connect to nutrics.db where all of the food information is stored
        self.engine = create_engine('sqlite:///nutrics.db', convert_unicode=True)
        self.metadata = MetaData(bind=self.engine)
        #select DURHAM table, and autoload the columns contained within it
        self.localfoods = Table('FOOD_TABLE', self.metadata, autoload=True)

    def seek_local(self, lat, lon):
        #this query sorts the nearest (lat / lon) 1000 items in the database in ascending order (closest first)
        #What it does: Every query gets a response. No matter how far away someone is from the nearest known item.
        #What it doesn't: Return queries ONLY within a certain radius. If you want this, you will need to look into Haversine formula. 

        query = select([self.localfoods.c.item_name, self.localfoods.c.embedding, self.localfoods.c.latitude]).order_by(asc(
            (lat-self.localfoods.c.latitude)*(lat-self.localfoods.c.latitude) + 
            (lon - self.localfoods.c.longitude)*(lon - self.localfoods.c.longitude)
            )).limit(1000)

        #connect to engine and execute the above query
        res = self.engine.connect().execute(query)

        #collect embeddings, item names, and keys (right now just float value of latitude) from the query
        embeddings = []
        item_names = []
        keys = []

        for i in res: 
            embedding = json.loads(i[1])
            embeddings.append(embedding)
            item_names.append(i[0])
            keys.append(i[2])

        #numpy arrays compile to c, which makes it much faster for cosine distance finding later
        numped = np.array(embeddings)

        #need all of this information to send full recommendation
        return numped, item_names, keys

    #method to select rows from database once the match has been made. This will return all information on an item (restaurant, desc, price, etc)
    def return_info(self, item_name, latitude): 
        query = select(['*']).where(self.localfoods.c.item_name == item_name and self.localfoods.c.latitude == latitude)
        res = self.engine.connect().execute(query)
        for i in res: 
            result = i
        return result
        
    #close unused connections to maintain lanes
    def close_connection(self): 
        self.engine.dispose()
        print("Connection closed.")