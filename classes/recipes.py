# recipes API CRUD operations

from flask import request, jsonify, make_response
from app.models import Users, Categories, Recipes
from flask.views import MethodView
from classes.auth.auth import token_required
import re


class NonFilteredRecipesManipulations(MethodView):
    """This will handle the POST and Get methods with no parameters
    """

    decorators = [token_required]

    def post(self, user_in_session, category_id):
        # This method will create and save a recipe
        """
       Create Recipe
       ---
       tags:
         - Recipes Endpoints
       parameters:
         - in: path
           name: category_id
           description: category_id
           type: integer
         - in: body
           name: Recipes details
           description: Create recipe by providing recipe name and description
           type: string
           required: true
           schema:
             id: create_recipes
             properties:
               recipe_name:
                 default: Ugali
               recipe_procedure:
                 default: Boil water; Put flour; mix the water and flour for five min; serve ugali.
       responses:
         201:
           description: Recipe created successfully
         409:
           description: Recipe exists!
         400:
           description: Invalid recipe name given
         404:
           description: Category not found
         422:
           description: Please fill all the fields
        """
        recipename = str(request.data.get('recipe_name', '')).strip()
        recipeprocedure = str(request.data.get('recipe_procedure', '')).strip()
        regexrecipe_name = "^[a-zA-Z0-9-+\s]{4,20}$"
        regexrecipe_procedure = "^[a-zA-Z0-9-+\s]{4,100}$"
        check_recipe_existence = Recipes.query.filter_by(users_id=user_in_session, category_id=category_id,
                                                         recipe_name=recipename).first()
        try:
            if recipename and recipeprocedure:
                if re.search(regexrecipe_name, recipename) or re.search(regexrecipe_procedure, recipeprocedure):
                    if not check_recipe_existence:

                        recipes_save = Recipes(recipe_name=recipename, recipe_description=recipeprocedure,
                                               category_id=category_id, users_id=user_in_session)
                        recipes_save.save()

                        return make_response(jsonify({'message': 'Recipe created successfully'})), 201
                    return make_response(jsonify({'message': 'Recipe exists!'})), 409
                return make_response(jsonify({'message': 'Invalid recipe name or procedure given'})), 400
            return make_response(jsonify({'message': 'Please fill all the fields'})), 422
        except Exception:
            return make_response(jsonify({'message': 'Category not found'})), 404

    def get(self, user_in_session, category_id):
        # This method will retrieve all the recipes under the category given

        """
           Retrieve recipes
           ---
           tags:
             - Recipes Endpoints
           parameters:
             - in: path
               name: category_id
               description: category id
               type: integer
               required: true

             - in: query
               name: q
               description: Search parameter
               type: string

             - in: query
               name: page
               description: page number
               type: integer
               default: 1

             - in: query
               name: limit
               description: Limit
               type: integer
               default: 10

           responses:
             201:
               description: Category created successfully
             400:
               description: Invalid page number or limit
             401:
               description: Recipe not found
             422:
               description: Please fill all the fields
                """

        page_number = request.args.get("page", default=1, type=int)
        no_items_per_page = request.args.get("limit", default=10, type=int)

        category_recipes = Recipes.get_all(category_id).paginate(page_number, no_items_per_page, error_out=False)
        recipe_list = []
        search_recipe = request.args.get('q')
        if search_recipe:
            search_recipes = Recipes.query.filter(Recipes.category_id == category_id,
                                                  Recipes.recipe_name.ilike('%' + search_recipe + '%')).\
                paginate(page_number, no_items_per_page, error_out=False)
            for recipes in search_recipes.items:
                searched_recipes = {
                    'id': recipes.id,
                    'recipe_name': recipes.recipe_name,
                    'recipe_description': recipes.recipe_description,
                    'category_id': recipes.category_id,
                    'date_created': recipes.created_at,
                    'date_updated': recipes.updated_at
                    }
                recipe_list.append(searched_recipes)

            if len(recipe_list) <= 0:
                return make_response(jsonify({'message': "Recipe with the character(s) not found"})), 401
            return make_response(jsonify(recipe_list)), 200

        for recipes in category_recipes.items:
            all_recipes = {
                'id': recipes.id,
                'recipe_name': recipes.recipe_name,
                'recipe_description': recipes.recipe_description,
                'category_id': recipes.category_id,
                'date_created': recipes.created_at,
                'date_updated': recipes.updated_at
                 }
            recipe_list.append(all_recipes)

        if len(recipe_list) <= 0:
            return make_response(jsonify({'message': "No recipes found for this category"})), 401
        return make_response(jsonify(recipe_list)), 200


class FilteredRecipesManipulations(MethodView):
    """This will handle the GET, PUT and DELETE methods with parameters
    """
    decorators = [token_required]

    def get(self, user_in_session, category_id, recipe_id):
        # Retrieve a specific recipe from cetegory given

        """
        Retrieve single recipe
       ---
       tags:
         - Recipes Endpoints
       parameters:
         - in: path
           name: category_id
           description: category_id
           type: integer
           required: true

         - in: path
           name: recipe_id
           description: Recipe id
           type: integer
           required: true
       responses:
         404:
           description: Recipe/category not found
        """
        single_recipe = Recipes.query.filter_by(users_id=user_in_session, category_id=category_id, id=recipe_id).first()
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

        """
        Edit single recipe
       ---
       tags:
         - Recipes Endpoints
       parameters:
         - in: path
           name: Category_id
           description: Category id
           type: integer
           required: true

         - in: path
           name: recipe_id
           description: Recipe id
           type: integer
           required: true

         - in: body
           name: recipe_name
           description: Recipe name
           type: string
           required: true
           schema:
             id: update_recipes
             properties:
               recipe_name:
                 default: Sembe
       responses:
             201:
               description: Recipe updated successfully
             409:
               description: Recipe exists!
             400:
               description: Invalid recipe name given
             401:
               description: Recipe/Category not found
             422:
               description: Please fill all the fields
        """
        recipename = str(request.data.get('recipe_name', '')).strip()
        regexrecipe_name = "^[a-zA-Z0-9-+\s]{4,20}$"
        recipe = Recipes.query.filter_by(users_id=user_in_session, id=recipe_id, category_id=category_id).first()
        if recipe:
            if recipename:
                if re.search(regexrecipe_name, recipename):
                    unique_recipe = Recipes.recipe_name_unique(recipe_name=recipename, category_id=category_id)
                    if not unique_recipe:

                        recipe.recipe_name = recipename
                        recipe.save()

                        return make_response(jsonify({'message': 'Recipe updated successfully'})), 201
                    return make_response(jsonify({'message': 'Recipe exists!'})), 409
                return make_response(jsonify({'message': 'Invalid recipe name given'})), 400
            return make_response(jsonify({'message': 'Please fill all the fields'})), 422
        return make_response(jsonify({'message': 'Recipe not found'})), 404

    def delete(self, user_in_session, category_id, recipe_id):
        """
          Delete a Recipe
          ---
          tags:
            - Recipes Endpoints
          parameters:
            - in: path
              name: category_id
              description: category_id
              type: integer
              required: true

            - in: path
              name: recipe_id
              description: Recipe id
              type: integer
              required: true
          responses:
            200:
              description: Recipe deleted
            401:
              description: Recipe not found
        """
        recipe = Recipes.query.filter_by(users_id=user_in_session, id=recipe_id, category_id=category_id).first()
        if recipe:
            recipe.delete()
            return make_response(jsonify({'message': 'Recipe deleted'})), 200
        return make_response(jsonify({'message': 'Recipe not found'})), 404


nonfiltered_recipes = NonFilteredRecipesManipulations.as_view('nonfiltered_recipes')
filtered_recipes = FilteredRecipesManipulations.as_view('filtered_recipes')
