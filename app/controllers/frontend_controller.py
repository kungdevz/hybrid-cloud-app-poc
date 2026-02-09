#!/usr/bin/env python
from flask import Blueprint, render_template, session, request, jsonify
import requests

frontend = Blueprint('frontend', 'frontend', static_folder='../static', template_folder='../templates')

API_BASE_URL = 'http://localhost:5000/users'

@frontend.route('/', methods=['GET'])
def home():
    """Home page with user management dashboard"""
    return render_template('index.html')

@frontend.route('/api/session/users', methods=['GET', 'POST'])
def manage_session_users():
    """Manage users in session"""
    if request.method == 'POST':
        # Store user list in session
        data = request.get_json()
        session['users'] = data.get('users', [])
        session.modified = True
        return jsonify({'success': True, 'message': 'Session updated'})
    else:
        # Get users from session
        users = session.get('users', [])
        return jsonify({'users': users})

@frontend.route('/api/session/clear', methods=['POST'])
def clear_session():
    """Clear session data"""
    session.clear()
    return jsonify({'success': True, 'message': 'Session cleared'})
