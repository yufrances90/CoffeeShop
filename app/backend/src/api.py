import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import requires_auth, \
    get_token_auth_header, verify_decode_jwt, check_permissions
from .admin.auth import \
    requires_admin_auth, \
    get_access_token_and_perm_arr
from .exceptions.error import AuthError
from .admin.api import \
    request_get_all_users, \
    request_get_all_roles

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES

'''
    GET /drinks
        - a public endpoint
        - contain only the drink.short() data representation
        - returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["GET"])
def get_all_drinks():

    drinks = Drink.query.all()

    if len(drinks) == 0:
        abort(404)

    formatted_drinks = [drink.short() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    })

'''
    GET /drinks-detail
        - require the 'get:drinks-detail' permission
        - contain the drink.long() data representation
        - returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=["GET"])
@requires_auth(permission='get:drinks-detail')
def get_drinks_details(permission):
   
    drinks = Drink.query.all()

    formatted_drinks = [drink.long() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    })


'''
    POST /drinks
        - require the 'post:drinks' permission
        - contain the drink.long() data representation
        - returns status code 200 and json {"success": True, "drinks": drink} where drink an 
        array containing only the newly created drink or appropriate status code 
        indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def create_new_drink(permission):

    request_data = json.loads(request.data)

    if request_data is None:
        abort(400)

    req_title = request_data['title']
    req_recipe = request_data['recipe']

    if req_title is None or req_recipe is None or len(req_recipe) == 0:
        abort(400)

    drink = Drink(title=req_title, recipe=json.dumps(req_recipe))

    try:
        
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })

    except Exception as e:

        print(e)

        abort(422)
    
    
'''
    PATCH /drinks/<id>
        where <id> is the existing model id
        - respond with a 404 error if <id> is not found
        - update the corresponding row for <id>
        - require the 'patch:drinks' permission
        - contain the drink.long() data representation
        - returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing 
        only the updated drink or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def update_drink_details(permission, drink_id):

    if drink_id is None:
        abort(404)

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if drink is None:
        abort(404)

    request_data = json.loads(request.data)

    if request_data is None:
        abort(400)

    req_title = request_data['title']
    req_recipe = request_data['recipe']

    if req_title is None or req_recipe is None or len(req_recipe) == 0:
        abort(400)

    try:
        
        drink.title = req_title
        drink.recipe = json.dumps(req_recipe)

        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except Exception as e:

        print(e)

        abort(422)

   
'''
    DELETE /drinks/<id>
        where <id> is the existing model id
        - respond with a 404 error if <id> is not found
        - delete the corresponding row for <id>
        - require the 'delete:drinks' permission
        - returns status code 200 and json {"success": True, "deleted": id} where id is the id of 
        the deleted record or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drink(permission, drink_id):

    if drink_id is None:
        abort(404)

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if drink is None:
        abort(404)

    try:
        
        drink.delete()

        return jsonify({
            'success': True,
            'deleted': drink_id
        })
    except Exception as e:

        print(e)

        abort(422)


    
'''
Admin Routes
'''

@app.route('/admin/users', methods=['GET'])
@requires_admin_auth(permission='read:users')
def get_users(permission):

    res = get_access_token_and_perm_arr()

    access_token = res['access_token']

    user_list = request_get_all_users(access_token)

    return jsonify({
        'success': True,
        'users': user_list
    })

@app.route('/admin/roles', methods=['GET'])
@requires_admin_auth(permission='read:roles')
def get_roles(permission):

    res = get_access_token_and_perm_arr()

    access_token = res['access_token']

    role_list = request_get_all_roles(access_token)

    return jsonify({
        'success': True,
        'users': role_list
    })



## Error Handling
'''
error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
        }), 422

'''
error handler for 404
'''
@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "resource not found"
        }), 404

'''
error handler for 400
'''
@app.errorhandler(400)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 400,
        "message": "bad request"
        }), 400

'''
error handler for AuthError
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False, 
        "error": error.status_code,
        "message": error.error
        }), error.status_code