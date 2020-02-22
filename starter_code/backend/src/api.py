import click, json, os, re, types
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from sqlalchemy import exc
from .database.models import db, setup_db, Drink
from .auth.auth import AuthError, requires_auth

## ---------------------------------------------------------
## Config
## ---------------------------------------------------------

app = Flask(__name__)
setup_db(app)
CORS(app)

@app.cli.command('dbdrop')
def db_drop():
    """Drops database from command line."""
    click.echo('Dropping all tables.')
    db.drop_all()

@app.cli.command('dbcreate')
def db_create():
    """Creates database from the command line."""
    click.echo('Creating all tables.')
    db.create_all()

## ---------------------------------------------------------
## Utils
## ---------------------------------------------------------

# Validates hex color input.
def is_valid_hex_color(color):
    return re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color)

# Checks for valid drink recipe part.
def is_valid_recipe_part(part):
    if type(part) is not dict:
        return False

    # Sets default number of parts.
    default_parts = 1 
    if 'color' not in part and not is_valid_hex_color(part['color']):
        return False
    if 'name' not in part:
        return False
    if 'parts' not in part and not is_integer(part['parts']):
        return False
    
    return True

## ---------------------------------------------------------
## ROUTES
## ---------------------------------------------------------

# Endpoint for short-form of drinks menu.
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()

    if not drinks:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    }), 200

# Endpoint for long form of drinks menu.
@app.route('/drinks-detail', methods=['GET'])
def get_drinks_detailed():
    drinks = Drink.query.all()
    if not drinks:
      abort(404)

    return jsonify({
      'success': True,
      'drinks': [drink.long() for drink in drinks],
    }), 200

'''
@TODO implement endpoint
    POST /drinks
        it should require the 'post:drinks' permission
'''

# Endpoint to add new drink.
@app.route('/drinks', methods=['POST'])
def insert_drink():
    data = request.get_json()

    if 'title' not in data and not data['title']:
        abort(422)
    if 'recipe' not in data:
        abort(422)
    if type(data['recipe']) is not list:
        abort(422)

    for recipe_part in data['recipe']:
        if not is_valid_recipe_part(recipe_part):
            abort(422)

    drink = Drink(title=data['title'], recipe=json.dumps(data['recipe']))
    drink.insert()

    return jsonify({
        'success': True,
        'drink': drink.long(),
    }), 200

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        it should require the 'patch:drinks' permission
'''
# Endpoint to update existing drink.
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
def update_drink(drink_id):
    if not drink_id:
        abort(404)

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if not drink:
        abort(404)

    data = request.get_json()

    if 'title' in data and data['title']:
        drink.title = data['title']

    if 'recipe' in data and type(data['recipe']) is list:
        for recipe_part in data['recipe']:
            if not is_valid_recipe_part(recipe_part):
                abort(422)
        drink.recipe = data['recipe']

    drink.update()

    return jsonify({
        'success': True,
        'drink': drink.long(),
    }), 200

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        it should require the 'delete:drinks' permission
'''
# Endpoint to delete drink object.
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
def delete_drink(drink_id):
    if not drink_id:
        abort(404)

    drink_to_delete = Drink.query.get(drink_id)
    if not drink_id:
        abort(404)

    drink_to_delete.delete()
    db.session.commit()

    return jsonify({
        'success': True,
        'delete': drink_id
    }), 200

## ---------------------------------------------------------
## Error Handling
## ---------------------------------------------------------
@app.errorhandler(401)
def not_authorized(error):
    return jsonify({
        "success": False, 
        "error": 401,
        "message": "Authentication error."
    }), 401

@app.errorhandler(422)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "Item not found."
    }), 404

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "Request could not be processed."
    }), 422
