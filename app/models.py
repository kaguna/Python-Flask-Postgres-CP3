# creates the user, categories and recipes tables schema

from app import db
import datetime

# import the db connection from the app/__init__.py


class Users(db.Model):
    """ This class represents the users table"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(1024))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp())
    categories = db.relationship('Categories', order_by='Categories.id', cascade="all, delete-orphan")

    def __init__(self, email, username, password):
        """initialize with user email."""
        self.email = email
        self.username = username
        self.password = password

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Users.query.all()

    def __repr__(self):
        return "<Users: {}>".format(self.email)


class Categories(db.Model):
    """ This class represents the recipe categories table"""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100))
    users_id = db.Column(db.Integer, db.ForeignKey(Users.id), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now,
                           onupdate=datetime.datetime.now)
    recipes = db.relationship('Recipes', order_by='Recipes.id', cascade="all, delete-orphan")

    def __init__(self, category_name, users_id):
        """initialize with category name and user id."""
        self.category_name = category_name
        self.users_id = users_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def name_unique(owner_id, category_name):
        check_category_existence = Categories.query.filter_by(
            category_name=category_name,
            users_id=owner_id).first()

        return check_category_existence

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all(owner_id):
        return Categories.query.filter_by(users_id=owner_id).order_by("id desc")

    def __repr__(self):
        return "<Categories: {}>".format(self.category_name)


class Recipes(db.Model):
    """ This class represents the recipes table"""

    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    recipe_name = db.Column(db.String(100))
    recipe_description = db.Column(db.String(1024))
    category_id = db.Column(db.Integer, db.ForeignKey(Categories.id), nullable=False)
    users_id = db.Column(db.Integer, db.ForeignKey(Users.id), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now,
                           onupdate=datetime.datetime.now)

    def __init__(self, recipe_name, recipe_description, category_id, users_id):
        """initialize with recipe details."""
        self.recipe_name = recipe_name
        self.recipe_description = recipe_description
        self.category_id = category_id
        self.users_id = users_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def recipe_name_unique(recipe_name, category_id):
        recipe_existence = Recipes.query.filter_by(
            recipe_name=recipe_name,
            category_id=category_id).first()

        return recipe_existence

    @staticmethod
    def get_all(category, user):
        return Recipes.query.filter_by(category_id=category, users_id=user).order_by("id desc")

    def __repr__(self):
        return "<Recipes: {}>".format(self.recipe_name)


class BlacklistToken(db.Model):
    """Save tokens after successful logout"""

    __tablename__ = 'blacklisted_tokens'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(1024))
    date_blacklisted = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, token):
        self.token = token

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return "<Token: {}>".format(self.token)
