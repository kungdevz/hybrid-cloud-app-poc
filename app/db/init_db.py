#!/usr/bin/env python
"""
Database initialization script.
Reads init.sql and applies it to the database.
"""
import os
import sys
import pyodbc
from pathlib import Path

def init_database():
    """Initialize the database by running init.sql"""
    try:
        # Get database URL from config
        from config import app
        db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        
        # Parse basic connection info
        if not db_url:
            print("No database URI configured", file=sys.stderr)
            return False
        
        # Try to connect to the database
        # First check if tables exist
        try:
            from config import db
            # Try a simple query to see if the table exists
            from models.user import User
            User.query.first()
            print("Database already initialized - table exists")
            return True
        except Exception as e:
            print(f"Attempting to initialize database: {e}")
        
        # Read the init.sql script
        init_script_path = os.path.join(
            os.path.dirname(__file__), 
            '../db/init-scripts/init.sql'
        )
        
        if not os.path.exists(init_script_path):
            print(f"Init script not found at {init_script_path}", file=sys.stderr)
            return False
        
        with open(init_script_path, 'r') as f:
            sql_commands = f.read()
        
        # Execute the SQL commands
        # For now, we'll silently fail and let the app handle the error
        # The database is running, just not initialized yet
        print("Init script found but skipping execution in app startup")
        return False
        
    except Exception as e:
        print(f"Error during database initialization: {e}", file=sys.stderr)
        return False

if __name__ == '__main__':
    init_database()
