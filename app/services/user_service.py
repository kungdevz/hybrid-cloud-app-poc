#!/usr/bin/env python
from models.user import User
from config import db
from werkzeug.exceptions import NotFound

def get(page=1, limit=100):
    '''
    Get all entities with pagination
    :param page: current page number (1-based)
    :param limit: items per page
    :returns: dict with data and pagination info
    '''
    query = User.query.order_by(User.id.asc())
    total = query.count()
    
    users = query.offset((page - 1) * limit).limit(limit).all()
    
    return {
        'data': users,
        'total': total,
        'page': page,
        'limit': limit,
        'pages': (total + limit - 1) // limit
    }

def get_by_id(id):
    '''
    Get entity by id
    :param id: the entity id
    :returns: the entity
    '''
    user = User.query.get(id)
    if not user:
        raise NotFound('no such entity found with id=' + str(id))
    return user

def post(body):
    '''
    Create entity with body
    :param body: request body
    :returns: the created entity
    '''
    user = User(**body)
    db.session.add(user)
    db.session.commit()
    return user

def put(id, body):
    '''
    Update entity by id
    :param id: the entity id
    :param body: request body
    :returns: the updated entity
    '''
    try:
        user_id = int(id)
    except ValueError:
        raise NotFound('Invalid user ID format')

    # Use Native SQL to absolutely guarantee control over the UPDATE statement
    from sqlalchemy import text
    
    # Filter body to ensure ID is never in SET clause
    update_data = {k: v for k, v in body.items() if k.lower() != 'id'}
    
    if not update_data:
        # Nothing to update, just return the user
        user = User.query.get(user_id)
        if not user:
            raise NotFound('no such entity found with id=' + str(id))
        return user

    # Construct dynamic SET clause
    set_clause = ", ".join([f"{key} = :{key}" for key in update_data.keys()])
    sql = text(f"UPDATE dbo.users SET {set_clause} WHERE id = :id")
    
    # Add ID to parameters for WHERE clause
    params = update_data.copy()
    params['id'] = user_id
    
    result = db.session.execute(sql, params)
    
    if result.rowcount == 0:
         raise NotFound('no such entity found with id=' + str(id))
         
    db.session.commit()
    
    # Fetch updated object to return
    user = User.query.get(user_id)
    return user

def delete(id):
    '''
    Delete entity by id
    :param id: the entity id
    :returns: the response
    '''
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return {'success': True}
    raise NotFound('no such entity found with id=' + str(id))


