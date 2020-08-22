from app import app
from app import db
from app import mng_goals
from app.models import User, Restaurant
from flask import request, jsonify
from passlib.hash import sha256_crypt
from flask_jwt_extended import create_access_token, create_refresh_token

@app.route('/users/register', methods=['POST'])
def register():
    try:
        request_json = request.json
        email = request_json['email']
        password = sha256_crypt.encrypt(request_json['password'])
        restaurant_name = request_json['restaurantName']
        restaurant_location = request_json['restaurantLocation']
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "User already exists"})
        else:
            restaurant = Restaurant(restaurantName=restaurant_name, restaurantLocation=restaurant_location)
            db.session.add(restaurant)
            db.session.commit()

            user = User(email=email, password=password, restaurantId=restaurant.restaurantId)
            db.session.add(user)
            db.session.commit()
            return jsonify({"message": "user successfully created"})
    except:
        return jsonify({"error", "cannot register user"})


@app.route('/users/login', methods=['POST'])
def login():
    try:
        email = request.json['email']
        password = request.json['password']
        current_user = User.query.filter_by(email=email).first()

        if not current_user:
            return jsonify({"error": "Invalid username or password"})

        if not sha256_crypt.verify(password, current_user.password):
            return jsonify({"error": "Invalid username or password"})

        access_token = create_access_token(identity=current_user.userId)
        refresh_token = create_refresh_token(identity=current_user.userId)
        mng_goals.populate_connector(current_user.userId)
        return jsonify({"access_token": access_token,
                        "refresh_token": refresh_token,
                        "user_id": current_user.userId})
    except:
        # frontend will ask to please try again later
        return jsonify({"error", "Cannot login user"})



