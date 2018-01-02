# categories API CRUD operations

from flask import request, jsonify, make_response
from app.models import Categories
from flask.views import MethodView
from classes.auth.auth import token_required
import re


class NonFilteredCategoryManipulations(MethodView):
    """This will handle the POST and Get methods with no parameters"""

    decorators = [token_required]

    def post(self, user_in_session):
        categoryname = str(request.data.get('category_name', '')).strip()
        regexcategory_name = "[a-zA-Z0-9- .]"
        users_id = user_in_session
        category_existence = Categories.query.filter_by(category_name=categoryname).first()
        if categoryname:
            if re.search(regexcategory_name, categoryname):
                if not category_existence:
                    categories = Categories(category_name=categoryname, users_id=users_id)
                    categories.save()
                    return make_response(jsonify({'message': 'Category created successfully'})), 201
                return make_response(jsonify({'message': 'Category exists!'})), 409
            return make_response(jsonify({'message': 'Invalid category name given'})), 400
        return make_response(jsonify({'message': 'Please fill all the fields'})), 422

    def get(self,user_in_session):
        all_categories = Categories.get_all(user_in_session)
        search = request.args.get('q')
        category_list = []

        if search:
            searched_categories = Categories.query.filter(Categories.users_id == user_in_session,
                                                          Categories.category_name.ilike('%' + search + '%'))
            if searched_categories:
                for categories in searched_categories:
                    obj = {
                            'id': categories.id,
                            'category_name': categories.category_name,
                            'user_id': categories.users_id,
                            'date_created': categories.created_at,
                            'date_updated': categories.updated_at
                            }
                    category_list.append(obj)
                if len(category_list) <= 0:
                    return make_response(jsonify({'message': "Category with the character(s) not found"})), 401
                return make_response(jsonify(category_list)), 200

        for categories in all_categories:
            obj = {
                'id': categories.id,
                'category_name': categories.category_name,
                'user_id': categories.users_id,
                'date_created': categories.created_at,
                'date_updated': categories.updated_at
            }
            category_list.append(obj)
        return make_response(jsonify(category_list)), 200


class FilteredCategoryManipulations(MethodView):
    """
    This will handle the GET, PUT and DELETE operations for a specific
        category filtered by ID
    """
    decorators = [token_required]

    def get(self,user_in_session, category_id):
        category = Categories.query.filter_by(id=category_id).first()
        if category:
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
        return make_response(jsonify({'message': 'Category not found'})), 401

    def put(self, user_in_session, category_id):
        category = Categories.query.filter_by(id=category_id).first()

        categoryname = str(request.data.get('category_name', '')).strip()
        regexcategory_name = "[a-zA-Z0-9- .]"
        category_existence = Categories.query.filter_by(category_name=categoryname).first()
        if category:
            if categoryname:
                if re.search(regexcategory_name, categoryname):
                    if not category_existence:

                        category.category_name = categoryname
                        category.save()

                        return make_response(jsonify({'message': 'Category updated successfully'})), 201
                    return make_response(jsonify({'message': 'Category exists!'})), 409
                return make_response(jsonify({'message': 'Invalid category name given'})), 400
            return make_response(jsonify({'message': 'Please fill all the fields'})), 422
        return make_response(jsonify({'message': 'Category not found'})), 401

    def delete(self, user_in_session, category_id):
        category = Categories.query.filter_by(id=category_id).first()
        if category:
            category.delete()
            return make_response(jsonify({'message': 'Category deleted'})), 200
        return make_response(jsonify({'message': 'Category not found'})), 401


filtered_category = FilteredCategoryManipulations.as_view('filtered_category')
nonfiltered_category = NonFilteredCategoryManipulations.as_view('nonfiltered_category')
