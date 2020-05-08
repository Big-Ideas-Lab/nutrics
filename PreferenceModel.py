'''
This file defines our Preference Model. It tracks and stores user preferences.
Created by Joshua D'Arcy on 4.10.2020.
'''

from run import db #import database connections
from datetime import datetime #for preference timestamps


class PreferenceModel(db.Model): 
    __tablename__ = 'user_preferences'

    #each row in the table has a username, preference, ID, and added date.
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), nullable = False)
    preference = db.Column(db.String(120), nullable = False)
    added = db.Column(db.DateTime, nullable=False)

    #save preference to database
    def save_to_db(self):
        try:
            db.session.add(self)
            db.session.commit()
            return {'message': 'Preference successfully added'}, 200
        except: 
            return {'message': 'Something went wrong. Try again.'}, 200
    
    #remove preference from database
    def remove_from_db(self): 
        try:
            db.session.query(PreferenceModel).filter(PreferenceModel.username==self.username).filter(PreferenceModel.preference == self.preference).delete()
            db.session.commit()
            return {'message': 'Preference successfully removed.'}, 200
        except:
            return {'message': 'There was an error with removing the preference. Either it does not exist or there was a string matching issue.'}

    #get list of all preferences from database for a given user (authentication required in UserResources.py)
    @classmethod
    def return_user_hx(cls, username): 
        def to_json(x): 
            return {
                'username': x.username,
                'preference': x.preference,
                'added': str(x.added)
            }
        return {'message': list(map(lambda x: to_json(x), PreferenceModel.query.filter_by(username = username).all()))}

    #admin data dump method to receive all preferences for all users (admin access required in AdminResources.py)
    @classmethod
    def data_dump(cls): 
        def to_json(x): 
            return {
                'username': x.username, 
                'preference': x.preference, 
                'timestamp': str(x.added)
            }
        return {'message': list(map(lambda x: to_json(x), PreferenceModel.query.all()))}