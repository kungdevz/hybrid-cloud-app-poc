#!/usr/bin/env python
import os
import yaml
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from urllib.parse import quote_plus

app = Flask(__name__)

# Load config
with open('config.yaml') as f:
    config_obj = yaml.load(f, Loader=yaml.Loader)

# Logic: Priority to Env Var, then Config File
database_uri = os.getenv('DATABASE_URI')
database_password = os.getenv('DATABASE_PASSWORD')
database_url = database_uri % quote_plus(database_password)

if not database_uri or not database_password:
    database_uri = config_obj.get('DATABASE_URI', '')
    database_password = config_obj.get('DATABASE_PASSWORD', '')
    database_url = database_uri % quote_plus(database_password)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)