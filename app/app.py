#!/usr/bin/env python
from config import app
from controllers.user_controller import api
from controllers.frontend_controller import frontend
from flask_session import Session

# Initialize session
Session(app)

# register the api and frontend blueprints
app.register_blueprint(api)
app.register_blueprint(frontend)

if __name__ == '__main__':
    ''' run application '''
    app.run(host='0.0.0.0', port=5000)
