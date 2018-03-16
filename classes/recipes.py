# This file provides the CRUD operations for the recipes.

from flask import request, jsonify, make_response
from app.models import Recipes, Categories
from flask.views import MethodView
from classes.auth.auth import token_required
import re


class NonFilteredRecipesManipulations(MethodView):
    """This will handle the POST and Get methods with no parameters
    """

    decorators = [token_required]
    regex_recipe_name = "^[a-zA-Z0-9-+\s]{4,20}$"

    @classmethod
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
        recipe_name = str(request.data.get('recipe_name', '')).strip()
        recipe_procedure = str(request.data.get('recipe_procedure', '')).strip()

        check_recipe_existence = Recipes.query.filter_by(users_id=user_in_session,
                                                         category_id=category_id).all()
        # This checks whether the catgory specified has the a similar category name from the user.
        if not recipe_name or not recipe_procedure:
            return make_response(jsonify({'message': 'Please fill all the fields'})), 400

        if not re.search(self.regex_recipe_name, recipe_name):
            return make_response(jsonify({'message': 'Invalid recipe name given'})), 400

        for recipe_in_list in check_recipe_existence:
            recipe_name_in_list = recipe_in_list.recipe_name
            if recipe_name.upper() == recipe_name_in_list.upper():
                return make_response(jsonify({'message': 'Recipe name exists!'})), 409

        recipes_save = Recipes(recipe_name=recipe_name, recipe_description=recipe_procedure,
                               category_id=category_id, users_id=user_in_session)
        recipes_save.save()
        # This saves the category after it passes all the conditions.

        return make_response(jsonify({'message': 'Recipe created successfully'})), 201


    @classmethod
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
        no_items_per_page = request.args.get("limit", default=8, type=int)
        search_recipe = request.args.get('q')
        # These are the arguments to be provided in the url
        check_category_exists = Categories.query.filter_by(id=category_id).first()
        category_recipes = Recipes.get_all(category_id, user_in_session).\
            paginate(page_number, no_items_per_page, error_out=True)
        # This retrieves all the recipes belonging to a specific category.
        recipe_list = []
        if check_category_exists:

            if search_recipe:
                # This filters the recipes when the user provides the search parameters q.
                search_recipes = Recipes.query.filter(Recipes.users_id == user_in_session,
                                                      Recipes.recipe_name.ilike('%' + search_recipe + '%')). \
                    paginate(page_number, no_items_per_page, error_out=False)
                for recipes in search_recipes.items:
                    # This loops retrieves all the recipes that match the search string.
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
                    # This checks whether the searched recipe list contains data.
                    return make_response(jsonify({'message': "Recipe does not exist."})), 404
                list_of_recipes = {'recipes': recipe_list, "total_items": search_recipes.total,
                                      "total_pages": search_recipes.pages, "current_page": search_recipes.page}
                return make_response(jsonify(list_of_recipes)), 200
            else:
                for recipes in category_recipes.items:
                    # This loops all the recipes of the category with no search parameters.
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
                    return make_response(jsonify({'message': "No recipes for this category."})), 402
                list_of_recipes = {'recipes': recipe_list, "total_items": category_recipes.total,
                                   "total_pages": category_recipes.pages, "current_page": category_recipes.page}
                return make_response(jsonify(list_of_recipes)), 200

        return make_response(jsonify({'message': "Category does not exist."})), 406


class FilteredRecipesManipulations(MethodView):
    """This will handle the GET, PUT and DELETE methods with parameters
    """
    decorators = [token_required]

    @classmethod
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
        check_category_exists = Categories.query.filter_by(id=category_id).first()
        single_recipe = Recipes.query.filter_by(users_id=user_in_session, id=recipe_id).first()
        if check_category_exists:
            if single_recipe:
                # This checks whether the provided recipe exists
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
            return make_response(jsonify({'message': 'Recipe does not exist'})), 404
        return make_response(jsonify({'message': 'Category not found.'})), 404

    @classmethod
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
           name: recipe
           description: Recipe details
           type: string
           required: true
           schema:
             id: update_recipes
             properties:
               recipe_name:
                 default: Ugali
               recipe_procedure:
                 default: Boil water; Put flour; mix the water and flour for five min; serve ugali.
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
        recipe_name = str(request.data.get('recipe_name', '')).strip()
        recipe_procedure = str(request.data.get('recipe_procedure', '')).strip()

        # The retrieve_recipe stores the result of recipe to be updated.
        check_category_exists = Categories.query.filter_by(id=category_id).first()
        if not check_category_exists:
            return make_response(jsonify({'message': 'Category not found.'})), 404

        retrieve_recipe = Recipes.query.filter_by(users_id=user_in_session,
                                                  id=recipe_id,
                                                  category_id=category_id).first()

        if recipe_name:

            if not retrieve_recipe:
                return make_response(jsonify({'message': 'Recipe does not exist.'})), 404

            if not re.search(NonFilteredRecipesManipulations.regex_recipe_name, recipe_name):
                return make_response(jsonify({'message': 'Invalid recipe name given'})), 400

            check_recipe_is_unique = Recipes.query.filter_by(category_id=category_id, users_id=recipe_id)
            for recipe_in_list in check_recipe_is_unique:
                recipe_name_in_list = recipe_in_list.recipe_name
                if recipe_name.upper() == recipe_name_in_list.upper():
                    # This checks whether the recipe exists in the specified category.
                    return make_response(jsonify({'message': 'Recipe name exists!'})), 409

            retrieve_recipe.recipe_name = recipe_name
            retrieve_recipe.save()
            # This saves the category name after update.
            return make_response(jsonify({'message': 'Recipe name updated successfully'})), 201
        if recipe_procedure:
            retrieve_recipe.recipe_description = recipe_procedure
            retrieve_recipe.save()
            # This saves the recipe procedure after update.
            return make_response(jsonify({'message': 'Recipe procedure updated successfully'})), 201
        return make_response(jsonify({'message': 'Please fill all the fields'})), 400



    @classmethod
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
        recipe = Recipes.query.filter_by(users_id=user_in_session, id=recipe_id).first()
        # The recipe variable stores the result if the specific recipe to be deleted.
        check_category_exists = Categories.query.filter_by(id=category_id).first()
        if not check_category_exists:
            return make_response(jsonify({'message': 'Category not found.'})), 404
        if recipe:
            recipe.delete()
            return make_response(jsonify({'message': 'Recipe deleted'})), 200
        return make_response(jsonify({'message': 'Recipe does not exist.'})), 404


non_filtered_recipes = NonFilteredRecipesManipulations.as_view('non_filtered_recipes')
filtered_recipes = FilteredRecipesManipulations.as_view('filtered_recipes')
