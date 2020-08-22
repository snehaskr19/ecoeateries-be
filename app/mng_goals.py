from app import app
from app import db
from app.models import User, Restaurant, Goal, Category, Connector

def get_all_goals():
    return Goal.query \
        .join(Category, Goal.categoryId == Category.categoryId) \
        .add_columns(Goal.goalId, Goal.goalName, Category.categoryName) \
        .all()

def populate_connector(user_id):
    goals = get_all_goals()
    
    restaurant_id = User.query.filter_by(userId=user_id).all().id

    for goal in goals:
        connector = Connector(restaurantId=restaurant_id, goalId=goal.id, status=0.0)
        db.session.add(connector)
        db.session.commit

        
    

