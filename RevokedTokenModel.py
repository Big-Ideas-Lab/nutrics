'''
This file defines our revoked token model. It keeps a blacklist of tokens once users are done with them.
Created by Joshua D'Arcy on 4/15/2020.
'''
import env
import os

from run import db
from passlib.hash import pbkdf2_sha256 as sha256
from datetime import datetime
from sqlalchemy import asc, desc
from sqlalchemy import select
from math import radians, cos, sin, asin, sqrt

from itsdangerous import URLSafeTimedSerializer

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