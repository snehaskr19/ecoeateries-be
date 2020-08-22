from app import app
from app import db
from app.models import User, Restaurant, Goal, Category, Connector


def get_all_goals():
    return Goal.query \
        .join(Category, Goal.categoryId == Category.categoryId) \
        .add_columns(Goal.goalId, Goal.goalName, Category.categoryName) \
        .all()


def get_user_goals(user_id):
    restaurant_id = User.query.filter_by(userId=user_id).first().restaurantId

    print("restaurantid: ", restaurant_id)
    restaurant_name = Restaurant.query.filter_by(restaurantId=restaurant_id).first().restaurantName
    print("restaurantname: ", restaurant_name)

    goals = Connector.query \
        .filter_by(restaurantId=restaurant_id) \
        .join(Goal, Goal.goalId == Connector.goalId) \
        .join(Category, Goal.categoryId == Category.categoryId) \
        .add_columns(Goal.goalName, Goal.goalId, Connector.status, Category.categoryName, Category.categoryId) \
        .all()

    print("goals: ", goals)

    goalsPerCategory = {}

    for goal in goals:
        goalDict = {
            'goalName': goal.goalName,
            'goalId': goal.goalId,
            'goalStatus': str(goal.status)
        }
        if goal.categoryName in goalsPerCategory.keys():
            goalsPerCategory[goal.categoryName][1].append(goalDict)
        else:
            goalsPerCategory[goal.categoryName] = [goal.categoryId, [goalDict]]

    categories = []

    for key, val in goalsPerCategory.items():
        category_dict = {
            'categoryName': key,
            'categoryId': val[0],
            'goals': val[1]
        }
        categories.append(category_dict)

    return {'restaurantName': restaurant_name, 'categories': categories}


def get_score_report(score_report):
    categories = score_report['categories']
    total_score = 0
    for category in categories:
        goals = category['goals']
        num_goals = 0
        category_score = 0
        for goal in goals:
            num_goals += 1
            category_score += float(goal['goalStatus'])
        category_percent = (category_score / num_goals) * 100
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
