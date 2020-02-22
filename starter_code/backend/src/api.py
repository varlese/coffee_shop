import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.models import db, setup_db, Drink
from .auth.auth import AuthError, requires_auth
import click


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
## ROUTES
## ---------------------------------------------------------

'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    print(drinks)
    
    if not drinks:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': drinks.short(),
    }), 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
# @app.route('/drinks-detail', methods=['GET'])
# def get_drinks():
#     drinks = Drink.query.all()
#     if not drinks:
#       abort(404)

#     return jsonify({
#       'success': True,
#       'drinks': drinks.long(),
#     }), 200

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

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
