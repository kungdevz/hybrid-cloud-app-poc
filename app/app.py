#!/usr/bin/env python
import time
from config import app, db
from controllers.user_controller import api
from controllers.frontend_controller import frontend
from flask_session import Session

# Initialize session
Session(app)

# register the api and frontend blueprints
app.register_blueprint(api)
app.register_blueprint(frontend)

def init_database():
    """Initialize database tables with retry logic for container environments."""
    max_retries = 10
    retry_delay = 5
    
    for attempt in range(1, max_retries + 1):
        try:
            with app.app_context():
                db.create_all()
                print("Database tables created successfully.")
                return True
        except Exception as e:
            print(f"Database init attempt {attempt}/{max_retries} failed: {e}")
            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    
    print("Warning: Could not initialize database tables. They may already exist or require manual setup.")
    return False

if __name__ == '__main__':
    ''' run application '''
    init_database()
    app.run(host='0.0.0.0', port=5000)
