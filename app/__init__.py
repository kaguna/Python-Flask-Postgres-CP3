# app/__init__.py

from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

# local import
from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()


def create_app(config_name):
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from app.models import Categories, Users
    from classes.categories import filtered_category, nonfiltered_category
    from classes.recipes import nonfiltered_recipes, filtered_recipes
    from classes.auth.users import user_creation, reset_password
    from classes.auth.login import user_login, user_logout

    """All the routes are handled here"""
    # user endpoints
    app.add_url_rule('/auth/register', methods=['POST'], view_func=user_creation)
    app.add_url_rule('/auth/login', methods=['POST'], view_func=user_login)
    app.add_url_rule('/auth/logout', methods=['POST'], view_func=user_logout)
    app.add_url_rule('/auth/reset_password', methods=['PUT'], view_func=reset_password)

    # category endpoints
    app.add_url_rule('/categories', methods=['GET', 'POST'], view_func=nonfiltered_category)
    app.add_url_rule('/category/<int:category_id>', methods=['GET', 'PUT', 'DELETE'], view_func=filtered_category)

    # recipes endpoints
    app.add_url_rule('/category/<int:category_id>/recipes', methods=['GET', 'POST'], view_func=nonfiltered_recipes)
    app.add_url_rule('/category/<int:category_id>/recipe/<int:recipe_id>', methods=['GET', 'PUT', 'DELETE'],
                     view_func=filtered_recipes)

    return app
