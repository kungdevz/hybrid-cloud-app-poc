---
description: Add a new feature module (Model, Service, Controller)
---

# Add New Module Workflow

Follow these steps to add a new feature module to the application.

## 1. Create the Model

Create `app/models/<entity>.py`:

```python
#!/usr/bin/env python
from config import db

class EntityName(db.Model):
    __tablename__ = 'entity_table'
    __table_args__ = {'schema': 'dbo'}
    
    id = db.Column(db.BigInteger(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    # Add more columns as needed
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
```

## 2. Create the Service

Create `app/services/<entity>_service.py`:

```python
#!/usr/bin/env python
from models.<entity> import EntityName
from config import db
from werkzeug.exceptions import NotFound

def get():
    return EntityName.query.all()

def get_by_id(id):
    return EntityName.query.get(id)

def post(body):
    entity = EntityName(**body)
    db.session.add(entity)
    db.session.commit()
    return entity

def put(body):
    entity = EntityName.query.get(body['id'])
    if entity:
        entity = EntityName(**body)
        db.session.merge(entity)
        db.session.commit()
        return entity
    raise NotFound(f'Entity not found with id={body["id"]}')

def delete(id):
    entity = EntityName.query.get(id)
    if entity:
        db.session.delete(entity)
        db.session.commit()
        return {'success': True}
    raise NotFound(f'Entity not found with id={id}')
```

## 3. Create the Controller

Create `app/controllers/<entity>_controller.py`:

```python
#!/usr/bin/env python
from flask import Blueprint, jsonify, request
import services.<entity>_service as entity_service
from models.<entity> import EntityName
from werkzeug.exceptions import HTTPException
import json

api = Blueprint('<entity>', '<entity>')

@api.route('/<entities>', methods=['GET'])
def api_get():
    entities = entity_service.get()
    return jsonify([e.as_dict() for e in entities])

@api.route('/<entities>', methods=['POST'])
def api_post():
    entity = entity_service.post(request.json)
    return jsonify(entity.as_dict())

@api.route('/<entities>/<string:id>', methods=['PUT'])
def api_put(id):
    body = request.json
    body['id'] = id
    res = entity_service.put(body)
    return jsonify(res.as_dict()) if isinstance(res, EntityName) else jsonify(res)

@api.route('/<entities>/<string:id>', methods=['DELETE'])
def api_delete(id):
    res = entity_service.delete(id)
    return jsonify(res)

@api.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    response.data = json.dumps({'success': False, 'message': e.description})
    response.content_type = 'application/json'
    return response
```

## 4. Register the Blueprint

Edit `app/app.py`:

```python
from controllers.<entity>_controller import api as entity_api

app.register_blueprint(entity_api)
```

## 5. Create Database Table

Option A - Add to `db/init-scripts/init.sql`:

```sql
IF OBJECT_ID(N'dbo.entity_table', N'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[entity_table] (
        [id] BIGINT IDENTITY(1,1) NOT NULL,
        [name] NVARCHAR(200) NOT NULL,
        CONSTRAINT [PK_entity_table] PRIMARY KEY CLUSTERED ([id] ASC)
    );
END;
GO
```

Option B - Use Flask-Migrate:

```bash
cd app
flask db migrate -m "Add entity_table"
flask db upgrade
```

## 6. Test the Endpoint

```bash
# GET all
curl http://localhost:5000/<entities>

# POST new
curl -X POST http://localhost:5000/<entities> \
  -H "Content-Type: application/json" \
  -d '{"name": "test"}'
```
