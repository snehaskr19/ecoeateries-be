"""

"""
from app import db
from app.models import User, Restaurant, Goal, Category, Connector
import jsonschema
from flask import jsonify


def update_goals(req):
    """

    :param req:
    :return:
    """
    try:
        status_schema = {
            "type": "object",
            "properties": {
                "goalId": {"type": "number"},
                "userId": {"type": "number"},
                "newStatus": {"type": "string"}
            },
        }
        request_json = req.json
        jsonschema.validate(instance=request_json, schema=status_schema)
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
    except jsonschema.exceptions.ValidationError as err:
        print(err)
    return jsonify({"error", "invalid request"})


def get_all_goals():
    """

    :return:
    """
    return Goal.query \
        .join(Category, Goal.categoryId == Category.categoryId) \
        .add_columns(Goal.goalId, Goal.goalName, Category.categoryName) \
        .all()


def get_user_goals(req):
    """

    :param req:
    :return:
    """
    user_id = req.args.get('userId')
    restaurant_id = User.query.filter_by(userId=user_id).first().restaurantId
    goals = query_user_goals(restaurant_id)
    goal_list = []
    for goal in goals:
        goal_dict = {
            'goalName': goal.goalName,
            'goalId': goal.goalId,
            'goalStatus': str(goal.status),
            'goalCategory': goal.categoryName
        }
        goal_list.append(goal_dict)
    return jsonify({'goalList': goal_list})


def query_user_goals(restaurant_id):
    """
    Fetches all user goals from the DB
    :param restaurant_id:
    :return:
    """
    goals = Connector.query \
        .filter_by(restaurantId=restaurant_id) \
        .join(Goal, Goal.goalId == Connector.goalId) \
        .join(Category, Goal.categoryId == Category.categoryId) \
        .add_columns(Goal.goalName, Goal.goalId, Goal.points, Connector.status, Category.categoryName, Category.categoryId) \
        .all()
    return goals


def generate_goal_report(user_id):
    """

    :param user_id:
    :return:
    """
    restaurant_id = User.query.filter_by(userId=user_id).first().restaurantId
    print("restaurantid: ", restaurant_id)
    restaurant_name = Restaurant.query.filter_by(restaurantId=restaurant_id).first().restaurantName
    print("restaurantname: ", restaurant_name)

    goals = query_user_goals(restaurant_id)
    print("goals: ", goals)

    goals_per_category = {}

    for goal in goals:
        goal_dict = {
            'goalName': goal.goalName,
            'goalId': goal.goalId,
            'goalStatus': str(goal.status),
            'goalPoints': goal.points
        }
        if goal.categoryName in goals_per_category.keys():
            goals_per_category[goal.categoryName][1].append(goal_dict)
        else:
            goals_per_category[goal.categoryName] = [goal.categoryId, [goal_dict]]

    categories = []

    for key, val in goals_per_category.items():
        category_dict = {
            'categoryName': key,
            'categoryId': val[0],
            'goals': val[1]
        }
        categories.append(category_dict)

    return {'restaurantName': restaurant_name, 'categories': categories}


def get_score_report(score_report):
    """

    :param score_report:
    :return:
    """
    categories = score_report['categories']
    total_score = 0
    for category in categories:
        goals = category['goals']
        num_goals = 0
        category_score = 0
        for goal in goals:
            num_goals += 1
            category_score += float(goal['goalStatus']) * goal['goalPoints']
        category_percent = (category_score / 20) * 100
        category['categoryScore'] = category_percent
        total_score += category_percent
    total_score_percent = total_score / len(categories)
    score_report['restaurantScore'] = total_score_percent
    return score_report


def populate_connector(user_id):
    """
        when user registers, all the static goals for the user are automatically set to have a status of 0
    """
    goals = get_all_goals()

    print(goals)

    restaurant_id = User.query.filter_by(userId=user_id).first().restaurantId

    for goal in goals:
        connector = Connector(restaurantId=restaurant_id, goalId=goal.goalId, status=0.0)
        db.session.add(connector)
        db.session.commit()
