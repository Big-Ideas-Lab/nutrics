'''
This file defines our data models.
Created by Joshua D'Arcy on 4/15/2020.
'''

from run import db
from passlib.hash import pbkdf2_sha256 as sha256
from datetime import datetime

class UserModel(db.Model):

    #establish table
    __tablename__ = 'users'

    # User information
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(120), unique = True, nullable = False)
    username = db.Column(db.String(120), unique = True, nullable = False)
    password = db.Column(db.String(120), nullable = False)

    age = db.Column(db.Integer, nullable = False)
    activity_level = db.Column(db.Integer, nullable = False)
    gender_identity = db.Column(db.Integer, nullable = False)

    admin = db.Column(db.Boolean, nullable = False)
    registered_on = db.Column(db.DateTime, nullable = False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    
    #save user to database
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    #lookup user
    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username = username).first()
    
    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email = email).first()

    #hash password 
    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)
    
    #verify hashed password
    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)
    
    #method to retrieve all users
    @classmethod
    def return_all_users(cls):
        def to_json(x):
            return {
                'username': x.username,
                'date_joined': x.joined,
                'role': x.role
            }
        return {'users': list(map(lambda x: to_json(x), UserModel.query.all()))}

    #method to delete all users
    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Something went wrong with deleting the users. Please try again.'}

#class for preferences model
class PreferenceModel(db.Model): 
    __tablename__ = 'user_preferences'

    #each row in the table has a username, preference, and ID
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), nullable = False)
    preference = db.Column(db.String(120), nullable = False)
    added = db.Column(db.String(120), nullable = False)

    #save preference to database
    #todo: add dates for preferences for analysis
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

    #get list of all preferences from database for a given user (authentication required)
    @classmethod
    def return_user_hx(cls, username): 
        def to_json(x): 
            return {
                'username': x.username,
                'preference': x.preference
            }
        return {'message': list(map(lambda x: to_json(x), PreferenceModel.query.filter_by(username = username).all()))}

    @classmethod
    def data_dump(cls): 
        def to_json(x): 
            return {
                'username': x.username, 
                'preference': x.preference, 
                'timestamp': x.added
            }
        return {'message': list(map(lambda x: to_json(x), PreferenceModel.query.all()))}

#security class to blacklist tokens
class RevokedTokenModel(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key = True)
    jti = db.Column(db.String(120))
    
    def add(self):
        db.session.add(self)
        db.session.commit()
    
    #class method decorator allows for JWT blacklist checking without instantiating class
    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti = jti).first()
        return bool(query)