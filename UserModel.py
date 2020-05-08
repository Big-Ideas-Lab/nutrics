'''
This file defines our User Model. It handles user creation, login, authentication for users and provides admin methods. 
Created by Joshua D'Arcy on 4.10.2020.
'''

import env
import os
from run import db
from passlib.hash import pbkdf2_sha256 as sha256 #for password encryption
from datetime import datetime 
from itsdangerous import URLSafeTimedSerializer #for serializing an email URL with authentication token

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
    
    #lookup email
    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email = email).first()

    #method to hash password with account creation
    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)
    
    #method to verify hashed password when users login
    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

    #Admin method to add admin privelages to a user
    @classmethod
    def make_admin(cls,username):
        new_admin = cls.query.filter_by(username=username).first()
        new_admin.admin = True
        db.session.commit()
        return {'message': 'updated {} to have admin privelages.'.format(username)}

    #Admin method to retrieve all user data.
    @classmethod
    def return_all_users(cls):
        def jsonit(x):
            return {
                'username': x.username,
                'email': x.email, 
                'age': x.age,
                'activity_level': x.activity_level, 
                'gender_identity': x.gender_identity,
                'date_joined': str(x.registered_on),
                'confirmed': x.confirmed,
                'date_confirmed': str(x.confirmed_on),
                'admin': x.admin
            }
        return {'users': list(map(lambda x: jsonit(x), UserModel.query.all()))}

    #Model method to generate an authentication token 
    @staticmethod
    def generate_confirmation_token(email):
        serializer = URLSafeTimedSerializer(os.getenv('URL_KEY'))
        return serializer.dumps(email, salt= os.getenv('URL_SALT'))

    #Model method to build email around an authentucation token
    @staticmethod
    def confirm_token(token, expiration=3600):
        serializer = URLSafeTimedSerializer(os.getenv('URL_KEY'))
        try:
            email = serializer.loads(
                token,
                salt=os.getenv('URL_SALT'),
                max_age=expiration
            )
        except:
            return False
        return email