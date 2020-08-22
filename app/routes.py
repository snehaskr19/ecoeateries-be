from app import app
from app import db
from app import mng_goals
from app.models import User, Restaurant, Connector, Goal, Category
from flask import request, jsonify
from passlib.hash import sha256_crypt
from flask_jwt_extended import create_access_token, create_refresh_token
import jsonschema


@app.route('/users/register', methods=['POST'])
def register():
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
        request_json = request.json
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


@app.route('/users/login', methods=['POST'])
def login():
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

@app.route('/restaurant-info', methods=['GET'])
def getUserRestaurantInfo():
    user_id = request.args.get('userId')
    restaurant_id = User.query.filter_by(userId=user_id).first().restaurantId
    restaurant = Restaurant.query.filter_by(restaurantId=restaurant_id).first()
    return jsonify(
        {
            'restaurantName': restaurant.restaurantName,
            'restaurantLocation': restaurant.restaurantLocation
        }
    )

@app.route('/report', methods=['GET'])
def getReport():
    user_id = request.args.get('userId')
    user_goals = mng_goals.get_user_goals(user_id)
    return jsonify(mng_goals.get_score_report(user_goals))



@app.route('/restaurants', methods=['GET'])
def getAllRestaurantInfo():
    restaurants = User.query \
        .join(Restaurant, Restaurant.restaurantId==User.restaurantId) \
        .add_columns(User.userId, Restaurant.restaurantName, Restaurant.restaurantLocation) \
        .all()
    
    print(restaurants)

    restaurantList = []
    for restaurant in restaurants:
        restaurantDict = {
            "userId": restaurant.userId, 
            "restaurantName": restaurant.restaurantName, 
            "restaurantLocation": restaurant.restaurantLocation
        }
        restaurantList.append(restaurantDict)
    return jsonify({"restaurants": restaurantList})

@app.route('/user/goals', methods=['POST','GET'])
def updateUserGoalStatus():
    if request.method == 'POST':
        request_json = request.json
        user_id = request_json['userId']
        goal_id = request_json['goalId']
        new_status = request_json['newStatus']
        restaurant_id = User.query.filter_by(userId=user_id).first().restaurantId
        connector = Connector.query.filter_by(restaurantId=restaurant_id, goalId=goal_id).first()
        connector.status = float(new_status)
        db.session.add(connector)
        db.session.commit()
        return jsonify(
            {'message': 'goal successfully updated'}
        )
    else:
        user_id = request.args.get('userId')
        restaurant_id = User.query.filter_by(userId=user_id).first().restaurantId
        goals = Connector.query \
        .filter_by(restaurantId=restaurant_id) \
        .join(Goal, Goal.goalId == Connector.goalId) \
        .join(Category, Goal.categoryId == Category.categoryId) \
        .add_columns(Goal.goalName, Goal.goalId, Connector.status, Category.categoryName) \
        .all()
        goalList = []
        for goal in goals:
            goalDict = {
                'goalName': goal.goalName,
                'goalId': goal.goalId,
                'goalStatus': str(goal.status),
                'goalCategory': goal.categoryName
            }
            goalList.append(goalDict)
        return jsonify({'goalList': goalList})

@app.route('/user/exists', methods=['GET'])
def checkIfUserExists():
    user_id = request.args.get('userId')
    exists = db.session.query(db.exists().where(User.userId == user_id)).scalar()
    print(exists)
    if exists:
        return jsonify({"exists": "true"})
    else:
        return jsonify({"exists": "false"})











