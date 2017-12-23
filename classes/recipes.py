# recipes API CRUD operations

from flask import request, jsonify, make_response
from app.models import Categories, Recipes
from flask.views import MethodView
from classes.auth.auth import token_required
import re


class NonFilteredRecipesManipulations(MethodView):
    """This will handle the POST and Get methods with no parameters
    """

    decorators = [token_required]

    def post(self, user_in_session, category_id):
        # This method will create and save a recipe
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

    def get(self, user_in_session, category_id):
        # This method will retrieve all the recipes under the category given
        category_recipes = Recipes.get_all(category_id)
        results = []
        for recipes in category_recipes:
            all_recipes = {
                'id': recipes.id,
                'recipe_name': recipes.recipe_name,
                'recipe_description': recipes.recipe_description,
                'category_id': recipes.category_id,
                'date_created': recipes.created_at,
                'date_updated': recipes.updated_at
            }
            results.append(all_recipes)
        response = jsonify(results)
        response.status_code = 200
        return response


class FilteredRecipesManipulations(MethodView):
    """This will handle the GET, PUT and DELETE methods with parameters
    """
    decorators = [token_required]

    def get(self, user_in_session, category_id, recipe_id):
        # Retrieve a specific recipe from cetegory given
        single_recipe = Recipes.query.filter_by(category_id=category_id, id=recipe_id).first()
        if single_recipe:
            one_recipe = {
                'id': single_recipe.id,
                'recipe_name': single_recipe.recipe_name,
                'recipe_description': single_recipe.recipe_description,
                'category_id': single_recipe.category_id,
                'date_created': single_recipe.created_at,
                'date_updated': single_recipe.updated_at
            }
            response = jsonify(one_recipe)
            response.status_code = 200
            return response
        return make_response(jsonify({'message': 'Recipe not found'})), 404

    def put(self, user_in_session, category_id, recipe_id):
        # Edit the recipe name from a given category
        recipename = str(request.data.get('recipe_name', '')).strip()
        regexrecipe_name = "[a-zA-Z0-9- .]"
        recipe = Recipes.query.filter_by(id=recipe_id, category_id=category_id).first()
        recipe_existence = Recipes.query.filter_by(recipe_name=recipename).first()
        if recipe:
            if recipename:
                if re.search(regexrecipe_name, recipename):
                    if not recipe_existence:

                        recipe.recipe_name = recipename
                        recipe.save()

                        return make_response(jsonify({'message': 'Recipe updated successfully'})), 201
                    return make_response(jsonify({'message': 'Recipe exists!'})), 409
                return make_response(jsonify({'message': 'Invalid recipe name given'})), 400
            return make_response(jsonify({'message': 'Please fill all the fields'})), 422
        return make_response(jsonify({'message': 'Recipe not found'})), 404

    def delete(self, user_in_session, category_id, recipe_id):
        recipe = Recipes.query.filter_by(id=recipe_id, category_id=category_id).first()
        if recipe:
            recipe.delete()
            return make_response(jsonify({'message': 'Recipe deleted'})), 200
        return make_response(jsonify({'message': 'recipe not found'})), 401


nonfiltered_recipes = NonFilteredRecipesManipulations.as_view('nonfiltered_recipes')
filtered_recipes = FilteredRecipesManipulations.as_view('filtered_recipes')
