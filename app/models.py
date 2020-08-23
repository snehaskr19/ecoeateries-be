"""
This module contains the framework for all the databases used in 
this project.
"""
from app import db


class User(db.Model):
    """
    Contains framework for users table:
        userId: int - primary key 
        emai: string
        password: string
        timestamp: string
        restaurantId: int - foreign key referencing restaurants table

    """
    __tablename__ = 'users'
    __table_args__ = {
        'autoload': True,
        'autoload_with': db.engine
    }


class Category(db.Model):
    """
    Contains framework for categories table:
        categoryId: int - primary key
        categoryName: string
    """
    __tablename__ = 'categories'
    __table_args__ = {
        'autoload': True,
        'autoload_with': db.engine
    }


class Connector(db.Model):
    """
    Contains framework for connector table:
        connectorId: int - primary key
        restaurantId: int - foreign key referencing restaurants table
        goalId: int - foreign key referencing goals table
        status: decimal

    """
    __tablename__ = 'connector'
    __table_args__ = {
        'autoload': True,
        'autoload_with': db.engine
    }


class Goal(db.Model):
    """
    Contains framework for goals table:
        goalId: int - primary key
        goalName: string
        points: int
        categoryId: int - foreign key referencing categories table

    """
    __tablename__ = 'goals'
    __table_args__ = {
        'autoload': True,
        'autoload_with': db.engine
    }


class Restaurant(db.Model):
    """
    Contains framework for restaurants table
        restaurantId: int - primary key
        restaurantName: string
        restaurantLocation: string
    """
    __tablename__ = 'restaurants'
    __table_args__ = {
        'autoload': True,
        'autoload_with': db.engine
    }
