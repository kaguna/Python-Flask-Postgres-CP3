# recipes API CRUD operations

from flask import request, jsonify, make_response
from app.models import Categories, Recipes
from flask.views import MethodView
from classes.auth.auth import token_required
import re


class FilteredRecipesManipulations(MethodView):
    """This will handle the POST and Get methods with no parameters"""

    decorators = [token_required]

    def post(self, user_in_session, category_id):
        recipename = str(request.data.get('recipe_name', '')).strip()
        recipeprocedure = str(request.data.get('recipe_procedure', '')).strip()
        regexrecipe_name = "[a-zA-Z0-9- .]"
        category = Categories.query.filter_by(id=category_id).first()
        recipe = Recipes.query.filter_by(recipe_name=recipename).first()
        if category:
            if recipename and recipeprocedure:
                if re.search(regexrecipe_name, recipename):
                    if not recipe:

                        recipes_save = Recipes(recipe_name=recipename, recipe_description=recipeprocedure,
                                               category_id=category_id)
                        recipes_save.save()

                        return make_response(jsonify({'message': 'Recipe created successfully'})), 201
                    return make_response(jsonify({'message': 'Recipe exists!'})), 409
                return make_response(jsonify({'message': 'Invalid recipe name given'})), 400
            return make_response(jsonify({'message': 'Please fill all the fields'})), 422
        return make_response(jsonify({'message': 'Category not found'})), 404


filtered_recipes = FilteredRecipesManipulations.as_view('filtered_recipes')
