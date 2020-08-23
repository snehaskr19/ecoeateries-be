"""

"""
from app import app
from app import db
from app.models import User, Restaurant
from flask import request, jsonify
from passlib.hash import sha256_crypt
from flask_jwt_extended import create_access_token, create_refresh_token
import jsonschema
from app import mng_goals


@app.route('/register', methods=['POST'])
def register():
    """ 
        Given a JSON object with user email, password, restaurant name, 
        and restaurant location, attempts to register users in the database.

    :return: a JSON object with success or error message
    """
    try:
        reg_schema = {
            "type": "object",
            "properties": {
                "email": {"type": "string"},
                "password": {"type": "string"},
                "restaurantName": {"type": "string"},
                "restaurantLocation": {"type": "string"}
            },
        }
        print(request)
        request_json = request.json
        print(request_json)
        jsonschema.validate(instance=request_json, schema=reg_schema)
        email = request_json['email']
        password = sha256_crypt.encrypt(request_json['password'])
        restaurant_name = request_json['restaurantName']
        restaurant_location = request_json['restaurantLocation']
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "User already exists"})
        else:
            # TODO: check whether restaurant exists before adding it to db for future mvp
            restaurant = Restaurant(restaurantName=restaurant_name, restaurantLocation=restaurant_location)
            db.session.add(restaurant)
            db.session.commit()

            user = User(email=email, password=password, restaurantId=restaurant.restaurantId)
            db.session.add(user)
            db.session.commit()

            mng_goals.populate_connector(user.userId)

            return jsonify({"message": "user successfully created"})
    except jsonschema.exceptions.ValidationError as err:
        print(err)
        return jsonify({"error", "invalid request"})
    except:
        return jsonify({"error", "cannot register user"})


@app.route('/login', methods=['POST'])
def login():
    """
    Given a JSON object with user email and password, validates user in database and 
    attempts to log in users.

    :return: if successful, a JSON object with a jwt token and user id; 
    else, a JSON object with an error message
    """
    try:
        lgn_schema = {
            "type": "object",
            "properties": {
                "email": {"type": "string"},
                "password": {"type": "string"},
            },
            "required": ["email", "password"]
        }
        req_json = request.json
        jsonschema.validate(instance=req_json, schema=lgn_schema)
        email = req_json['email']
        password = req_json['password']
        current_user = User.query.filter_by(email=email).first()

        if not current_user:
            return jsonify({"error": "Invalid username or password"})

        if not sha256_crypt.verify(password, current_user.password):
            return jsonify({"error": "Invalid username or password"})

        access_token = create_access_token(identity=current_user.userId)
        refresh_token = create_refresh_token(identity=current_user.userId)
        return jsonify({"access_token": access_token,
                        "refresh_token": refresh_token,
                        "user_id": current_user.userId})
    except jsonschema.exceptions.ValidationError as err:
        print(err)
        return jsonify({"error", "invalid request"})
    except:
        return jsonify({"error", "Cannot login user"})


@app.route('/user/restaurant-info', methods=['GET'])
def get_user_restaurant_info():
    """
    Given a user id as a query parameter, gets restaurant information for the user.

    :return: JSON object with restaurant name and location
    """
    user_id = request.args.get('userId')
    print(user_id)
    restaurant_id = User.query.filter_by(userId=user_id).first().restaurantId
    restaurant = Restaurant.query.filter_by(restaurantId=restaurant_id).first()
    return jsonify(
        {
            'restaurantName': restaurant.restaurantName,
            'restaurantLocation': restaurant.restaurantLocation
        }
    )


@app.route('/user/report', methods=['GET'])
def get_report():
    """
    Given a user id as a query parameter, gets a report with user sustainability progress info.

    :return: JSON object with user score, category info and score, and goal info and status
    """
    user_id = request.args.get('userId')
    user_goals = mng_goals.get_user_goals(user_id)
    return jsonify(mng_goals.get_score_report(user_goals))


@app.route('/user/timestamp', methods=['POST', 'GET'])
def access_timestamp():
    """
    If POST:
        given JSON object with user id and timestamp, update the timestamp field in the database
    If GET:
        given a user id, get timestamp field from database

    :return: if post: a JSON object with a success or error message; if get: a JSON object with timestamp
    """
    if request.method == 'POST':
        return update_timestamp(request)
    else:
        user_id = request.args.get('userId')
        timestamp = User.query.filter_by(userId=user_id).first().timestamp
        return jsonify({"timeStamp": timestamp})


@app.route('/restaurants', methods=['GET'])
def get_all_restaurant_info():
    """
    Gets a list of all restaurant info from the database

    :return: a JSON object with a list of restaurant names, restaurant locations, and user ids
    """
    restaurants = User.query \
        .join(Restaurant, Restaurant.restaurantId == User.restaurantId) \
        .add_columns(User.userId, Restaurant.restaurantName, Restaurant.restaurantLocation) \
        .all()
    print(restaurants)
    restaurant_list = []
    for restaurant in restaurants:
        restaurant_dict = {
            "userId": restaurant.userId,
            "restaurantName": restaurant.restaurantName,
            "restaurantLocation": restaurant.restaurantLocation
        }
        restaurant_list.append(restaurant_dict)
    return jsonify({"restaurants": restaurant_list})


@app.route('/user/goals', methods=['POST', 'GET'])
def access_goals():
    """

    :return:
    """
    if request.method == 'POST':
        return mng_goals.update_goals(request)
    else:
        return mng_goals.get_goals(request)


@app.route('/user/exists', methods=['GET'])
def check_if_user_exists():
    """

    :return:
    """
    user_id = request.args.get('userId')
    exists = db.session.query(db.exists().where(User.userId == user_id)).scalar()
    print(exists)
    if exists:
        return jsonify({"exists": "true"})
    else:
        return jsonify({"exists": "false"})


def update_timestamp(req):
    """

    :param req:
    :return:
    """
    try:
        ts_schema = {
            "type": "object",
            "properties": {
                "userId": {"type": "number"},
                "timeStamp": {"type": "string"}
            },
        }
        req_json = req.json
        jsonschema.validate(instance=req_json, schema=ts_schema)
        user_id = req_json['userId']
        user = User.query.filter_by(userId=user_id).first()
        time_stamp = req_json['timeStamp']
        user.timestamp = time_stamp
        db.session.add(user)
        db.session.commit()
        return jsonify(
            {'message': 'timestamp successfully updated'}
        )
    except jsonschema.ValidationError as err:
        print(err)
        return jsonify({"error": "invalid request"})
