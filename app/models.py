from app import db


class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {
        'autoload': True,
        'autoload_with': db.engine
    }


class Category(db.Model):
    __tablename__ = 'categories'
    __table_args__ = {
        'autoload': True,
        'autoload_with': db.engine
    }


class Connector(db.Model):
    __tablename__ = 'connector'
    __table_args__ = {
        'autoload': True,
        'autoload_with': db.engine
    }


class Goal(db.Model):
    __tablename__ = 'goals'
    __table_args__ = {
        'autoload': True,
        'autoload_with': db.engine
    }


class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    __table_args__ = {
        'autoload': True,
        'autoload_with': db.engine
    }
