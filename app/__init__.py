"""
Contains flask app setup 
"""
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
db = SQLAlchemy(app)

jwt = JWTManager(app)

from app import routes, models
