#!/usr/bin/env python
from flask import Blueprint, jsonify, request
import services.user_service as user_service
from models.user import User
from werkzeug.exceptions import HTTPException
import json

api = Blueprint('users', 'users')

@api.route('/users', methods=['GET'])
def api_get():
    ''' Get entities with pagination'''
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 100))
    except ValueError:
        page = 1
        limit = 100
        
    result = user_service.get(page, limit)
    
    return jsonify({
        'users': [user.as_dict() for user in result['data']],
        'meta': {
            'page': result['page'],
            'limit': result['limit'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@api.route('/users/<string:id>', methods=['GET'])
def api_get_by_id(id):
    ''' Get entity by id'''
    user = user_service.get_by_id(id)
    return jsonify(user.as_dict())

@api.route('/users', methods=['POST'])
def api_post():
    ''' Create entity'''
    user = user_service.post(request.json)
    return jsonify(user.as_dict())

@api.route('/users/<string:id>', methods=['PUT'])
def api_put(id):
    ''' Update entity by id'''
    body = request.json
    # Remove id from body to avoid accidental update
    if 'id' in body:
        del body['id']
    res = user_service.put(id, body)
    return jsonify(res.as_dict()) if isinstance(res, User) else jsonify(res)

@api.route('/users/<string:id>', methods=['DELETE'])
def api_delete(id):
    ''' Delete entity by id'''
    res = user_service.delete(id)
    return jsonify(res)

@api.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON format for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        'success': False,
        "message": e.description
    })
    response.content_type = "application/json"
    return response