#!/usr/bin/env python
import os
import re
import yaml
import tempfile
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from urllib.parse import quote_plus

app = Flask(__name__)

# Session Configuration - Use temp directory with unique path per pod
session_dir = os.path.join(tempfile.gettempdir(), 'flask_session')
os.makedirs(session_dir, exist_ok=True)

app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = session_dir
app.config['SESSION_FILE_THRESHOLD'] = 200
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes

# Load config
with open('config.yaml') as f:
    config_obj = yaml.load(f, Loader=yaml.Loader)

# Profile-based configuration (local, test, production)
# Priority: SQLALCHEMY_DATABASE_URI env var > PROFILE-based config > default (production)
profile = os.getenv('PROFILE', os.getenv('APP_PROFILE', 'production')).lower()

# Check for direct SQLALCHEMY_DATABASE_URI override first
sqlalchemy_database_uri = os.getenv('SQLALCHEMY_DATABASE_URI')

if sqlalchemy_database_uri:
    # Direct URI from environment (no password substitution needed)
    database_url = sqlalchemy_database_uri
else:
    # Profile-based database configuration
    database_configs = {
        'local': {
            'uri': 'mssql+pyodbc://sa:%s@database:1433/master?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes',
            'password': 'c2E6U2VjcmV0I1Bhc3MxMjM='
        },
        'test': {
            'uri': 'mssql+pyodbc://sa:%s@database:1433/master?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes',
            'password': 'c2E6U2VjcmV0I1Bhc3MxMjM='
        },
        'production': {
            'uri': config_obj.get('DATABASE_URI', ''),
            'password': config_obj.get('DATABASE_PASSWORD', '')
        }
    }

    # Get config for the current profile, fallback to production
    db_config = database_configs.get(profile, database_configs['production'])
    
    # Allow env var override for password
    database_uri = os.getenv('DATABASE_URI', db_config['uri'])
    database_password = os.getenv('DATABASE_PASSWORD', db_config['password'])
    
    database_url = database_uri % quote_plus(database_password)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


def get_odbc_connection_string(database: str = 'master') -> str:
    """Build a raw ODBC connection string from the current profile config.

    Reuses the same credentials and host already resolved above so that
    init_db.py doesn't need to re-parse the SQLAlchemy URI.

    Args:
        database: Target database name. Defaults to 'master' so that
            init scripts can run CREATE DATABASE statements.

    Returns:
        An ODBC connection string suitable for pyodbc.connect().
    """
    sa_uri: str = app.config.get('SQLALCHEMY_DATABASE_URI', '')

    pattern = re.compile(
        r'mssql\+pyodbc://(?P<user>[^:]+):(?P<password>[^@]+)'
        r'@(?P<host>[^:]+):(?P<port>\d+)/(?P<db>[^?]+)'
        r'(?:\?(?P<params>.*))?'
    )
    match = pattern.match(sa_uri)
    if not match:
        raise ValueError(f"Cannot parse database URI: {sa_uri}")

    user = match.group('user')
    password = match.group('password')
    host = match.group('host')
    port = match.group('port')
    params = match.group('params') or ''

    driver = 'ODBC Driver 18 for SQL Server'
    for param in params.split('&'):
        if param.lower().startswith('driver='):
            driver = param.split('=', 1)[1].replace('+', ' ')
            break

    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={host},{port};"
        f"DATABASE={database};"
        f"UID={user};"
        f"PWD={password};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=yes;"
    )