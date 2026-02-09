#!/usr/bin/env python
from flask import Flask, jsonify, request
from config import db
import yaml
import os

class User(db.Model):
    ''' The data model for MSSQL '''
    __tablename__ = 'users'
    __table_args__ = {'schema': 'dbo'}
    
    # BIGINT in MSSQL corresponds to your SQL script (bigint(20))
    id = db.Column(db.BigInteger(), primary_key=True, autoincrement=True)
    
    # Use String(200) - Flask-SQLAlchemy will map this to NVARCHAR(200)
    handle = db.Column(db.String(200), nullable=False)

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}