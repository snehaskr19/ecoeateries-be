from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

jwt = JWTManager(app)

from app import routes, models
