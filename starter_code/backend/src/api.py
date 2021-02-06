import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()


'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_all_drinks():
    try:
      drinks=Drink.query.all()
      return jsonify({
        'success' : True,
        'drinks' : [drink.short() for drink in drinks]
       })
    except:
        abort(404)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_all_drinks_detailed(payload):
    drinks=Drink.query.all()
    if(len(drinks)==0):
        abort(404)
        
    return jsonify({
        'success' : True,
        'drinks' : [drink.long() for drink in drinks]
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks",methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    body=request.get_json()
    new_title=body.get('title')
    new_recipe=body.get('recipe')
    if not (new_title or new_recipe):
        abort(400)

    try:
      drink=Drink(
        title=new_title,
        recipe=json.dumps(new_recipe)
      )
      drink.insert()
      return jsonify({
        'success' : True,
        'drinks' : [drink.long()]
      })
    except:
        abort(422)


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
@app.route("/drinks/<id>",methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload,id):
    try:
        drink=Drink.query.filter(Drink.id==id).one_or_none()
        if(drink is None):
            abort(404)

        body=request.get_json()
        up_title=body.get('title')
        up_recipe=body.get('recipe')
        if up_title:
         drink.title=up_title

        if up_recipe:
         drink.recipe=json.dumps(up_recipe)

        drink.update()
        return jsonify({
            'success' : True,
            'drinks' : [drink.long()]
        })
    except:
        abort(422)

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
@app.route("/drinks/<id>",methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload,id):
    try:
        drink=Drink.query.filter(Drink.id==id).one_or_none()
        drink.delete()
        if(drink is None):
            abort(404)

        return jsonify({
            'success' : True,
            'delete' : id
        })
    except:
        abort(422)

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success" : False, 
                    "error" : 422,
                    "message" : "unprocessable"
                    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
      'success': False,
      'error':404,
      'message': "resource not found"
    }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
      'success' : False,
      'error' : 400,
      'message' : "bad request"
    }), 400

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
      'success' : False,
      'error' : 405,
      'message' : "This method is not allowed"
    }), 405

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def handle_auth0_errors(e):
     return jsonify({
         'success' : False,
         'error' : e.status_code,
         'message' : e.error
     }), e.status_code
