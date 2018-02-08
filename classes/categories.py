# This file provides the categories CRUD operations.

from flask import request, jsonify, make_response
from app.models import Categories
from flask.views import MethodView
from classes.auth.auth import token_required
import re


class NonFilteredCategoryMethods(MethodView):
    """This will handle the POST and Get methods with no parameters
    """

    decorators = [token_required]
    regex_category_name = "^[a-zA-Z0-9-+\s]{4,20}$"

    @classmethod
    def post(self, user_in_session):
        """
       Create category
       ---
       tags:
         - Categories Endpoints
       parameters:
         - in: body
           name: Category details
           description: Create category by providing category name
           type: string
           required: true
           schema:
             id: create_categories
             properties:
               category_name:
                 default: Lunch
       responses:
         201:
           description: Category created successfully
         409:
           description: Category exists!
         400:
           description: Invalid category name given
         422:
           description: Please fill all the fields
        """
        category_name = str(request.data.get('category_name', '')).strip().lower()
        check_category_exist = Categories.query.filter_by(users_id=user_in_session,
                                                          category_name=category_name).first()

        if not category_name:
            return make_response(jsonify({'message': 'Please fill all the fields'})), 400

        if not re.search(self.regex_category_name, category_name):
            # This checks whether the category name matches the pattern specified.
            return make_response(jsonify({'message': 'Invalid category name given'})), 400

        if check_category_exist:
            return make_response(jsonify({'message': 'Category exists!'})), 409

        categories = Categories(category_name=category_name, users_id=user_in_session)
        categories.save()
        # This saves the new categories after it passes all the conditions.
        return make_response(jsonify({'message': 'Category created successfully'})), 201

    @classmethod
    def get(self, user_in_session):
        """
           Retrieve categories
           ---
           tags:
             - Categories Endpoints
           parameters:
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
             409:
               description: Category exists!
             400:
               description: Invalid category name given
             422:
               description: Please fill all the fields
        """
        page_number = int(request.args.get("page", default=1, type=int))
        no_items_per_page = int(request.args.get("limit", default=10, type=int))

        all_categories = Categories.get_all(user_in_session).paginate(
            page_number, no_items_per_page, error_out=False)
        # The all_categories variables stores all the categories
        #   belonging to the current user in session.

        search = request.args.get('q')
        category_list = []

        if search:
            # This filters the categories when user provides a search parameter q.
            searched_categories = Categories.query.filter(Categories.users_id == user_in_session,
                                                          Categories.category_name.ilike('%' + search + '%')).\
                paginate(page_number, no_items_per_page, error_out=False)
            # The searched_categories stores the result of search.
            if searched_categories:
                for categories in searched_categories.items:
                    # This loops all the categories matching the search parameter.
                    obj = {
                            'id': categories.id,
                            'category_name': categories.category_name,
                            'user_id': categories.users_id,
                            'date_created': categories.created_at,
                            'date_updated': categories.updated_at
                            }
                    category_list.append(obj)
                if len(category_list) <= 0:
                    # This checks whether the list contains data.
                    return make_response(jsonify({'message': "Category does not exist."})), 401
                return make_response(jsonify(category_list)), 200

        for categories in all_categories.items:
            # This loops all the categories of the user in session when the search
            #   parameter has not been provided.
            obj = {
                'id': categories.id,
                'category_name': categories.category_name,
                'user_id': categories.users_id,
                'date_created': categories.created_at,
                'date_updated': categories.updated_at
            }
            category_list.append(obj)
        if len(category_list) <= 0:
            # This checks whether the user has categories created.
            return make_response(jsonify({'message': "No categories for you."})), 401
        return make_response(jsonify(category_list)), 200


class FilteredCategoryMethods(MethodView):
    """This will handle the GET, PUT and DELETE operations for a specific
        category filtered by ID
    """
    decorators = [token_required]

    @classmethod
    def get(self, user_in_session, category_id):
        """
       Retrieve single category
       ---
       tags:
         - Categories Endpoints
       parameters:
         - in: path
           name: category_id
           description: category_id
           type: integer
       responses:
         401:
           description: Category not found
        """
        category = Categories.query.filter_by(users_id=user_in_session, id=category_id).first()
        if category:
            # This checks whether a specified category exists in the database.
            category_attributes = {
                'id': category.id,
                'category_name': category.category_name,
                'user_id': category.users_id,
                'date_created': category.created_at,
                'date_updated': category.updated_at
            }
            response = jsonify(category_attributes)
            response.status_code = 200
            return category_attributes
        return make_response(jsonify({'message': 'Category does not exist.'})), 404

    @classmethod
    def put(self, user_in_session, category_id):
        """
       Edit single category
       ---
       tags:
         - Categories Endpoints
       parameters:
         - in: path
           name: Category_id
           description: Category id
           type: integer
         - in: body
           name: category_name
           description: Category name
           type: string
           required: true
           schema:
             id: edit_categories
             properties:
               category_name:
                 default: Supper
       responses:
             201:
               description: Category updated successfully
             409:
               description: Category exists!
             400:
               description: Invalid category name given
             401:
               description: Category not found
             422:
               description: Please fill all the fields
        """

        category_name = str(request.data.get('category_name', '')).strip().lower()
        retrieve_the_category = Categories.query.filter_by(users_id=user_in_session,
                                                           id=category_id).first()
        # The retrieve_the_category stores the specific retrieved
        #   category for the user in session.
        if not retrieve_the_category:
            return make_response(jsonify({'message': 'Category does not exist.'})), 404

        if not category_name:
            return make_response(jsonify({'message': 'Please fill all the fields'})), 400

        if not re.search(NonFilteredCategoryMethods.regex_category_name, category_name):
            return make_response(jsonify({'message': 'Invalid category name given'})), 400

        check_is_category_unique = Categories.name_unique(category_name=category_name,
                                                          owner_id=user_in_session)
        # The check_is_category_unique returns true when a similar category
        #   name is found and false when it does not exist.
        if check_is_category_unique:
            return make_response(jsonify({'message': 'Category name exists!'})), 409

        retrieve_the_category.category_name = category_name
        # This updates the category name with the newly provided name.
        retrieve_the_category.save()
        # The changes after the update are then stored.
        return make_response(jsonify({'message': 'Category updated successfully'})), 201

    @classmethod
    def delete(self, user_in_session, category_id):
        """
       Delete a category
       ---
       tags:
         - Categories Endpoints
       parameters:
         - in: path
           name: category_id
           description: category_id
           type: integer
       responses:
         200:
           description: Category deleted
         401:
           description: Category not found
        """
        retrieve_category_to_delete = Categories.query.filter_by(users_id=user_in_session,
                                                                 id=category_id).first()
        if not retrieve_category_to_delete:
            # This checks whether the category whose id provided exists.
            return make_response(jsonify({'message': 'Category does not exist.'})), 404

        retrieve_category_to_delete.delete()
        # If the category exists, it is deleted.
        return make_response(jsonify({'message': 'Category deleted successfully.'})), 200


filtered_category = FilteredCategoryMethods.as_view('filtered_category')
non_filtered_category = NonFilteredCategoryMethods.as_view('non_filtered_category')
