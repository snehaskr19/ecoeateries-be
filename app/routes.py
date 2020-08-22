from app import app
from app.models import User, Restaurant
from flask import request, jsonify
from passlib.hash import sha256_crypt

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/users/register', method=['POST'])
def register():
    request_json = request.json
    email = request_json['email']
    password = sha256_crypt.encrypt(request_json['password'])
    restaurantName = request_json['restaurantName']
    restaurantLocation = request_json['restaurantLocation']
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "user already exists"})
    else:
        restaurant = Restaurant(restaurantName=restaurantName, restaurantLocation=restaurantLocation)
        db.session.add(restaurant)
        db.session.commit()

        user = User(email=email, password=password, restaurantId=restaurant.id)
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "user successfully created"})








