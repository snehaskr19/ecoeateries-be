from app import app
from app import db
from app.models import User, Restaurant, Goal, Category, Connector


def get_all_goals():
    return Goal.query \
        .join(Category, Goal.categoryId == Category.categoryId) \
        .add_columns(Goal.goalId, Goal.goalName, Category.categoryName) \
        .all()


def populate_connector(user_id):
    """
        when user registers, all the static goals for the user are automatically set to have a status of 0
    """
    goals = get_all_goals()

    restaurant_id = User.query.filter_by(userId=user_id).first().restaurantId

    for goal in goals:
        connector = Connector(restaurantId=restaurant_id, goalId=goal.goalId, status=0.0)
        db.session.add(connector)
        db.session.commit()


