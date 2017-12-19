# categories API CRUD operations

from flask import request, jsonify, make_response
from app.models import Categories
from flask.views import MethodView
from classes.auth.auth import token_required


class NonFilteredCategoryManipulations(MethodView):
    """This will handle the POST and Get methods with no parameters"""

    decorators = [token_required]

    def post(self, user_in_session):
        category_name = str(request.data.get('category_name', ''))
        # users_id = str(request.data.get('users_id', ''))
        users_id = user_in_session
        if category_name:
            categories = Categories(category_name=category_name, users_id=users_id)
            categories.save()

            return make_response(jsonify({'message': 'Category created successfully'})), 201

    def get(self,user_in_session):
        all_categories = Categories.get_all(user_in_session)
        results = []

        for categories in all_categories:
            obj = {
                'id': categories.id,
                'category_name': categories.category_name,
                'user_id': categories.users_id,
                'date_created': categories.created_at,
                'date_updated': categories.updated_at
            }
            results.append(obj)
        response = jsonify(results)
        response.status_code = 200
        return response


class FilteredCategoryManipulations(MethodView):
    """
    This will handle the GET, PUT and DELETE operations for a specific
        category filtered by ID
    """
    def get(self, category_id):
        category = Categories.query.filter_by(id=category_id).first()
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

    def put(self, category_id):
        category = Categories.query.filter_by(id=category_id).first()
        if category:
            category_name = str(request.data.get('category_name', ''))
            category.category_name = category_name
            category.save()
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
        return make_response(jsonify({'message': 'Category not authenticated'})), 401

    def delete(self, category_id):
        category = Categories.query.filter_by(id=category_id).first()
        if category:
            category.delete()
            return make_response(jsonify({'message': 'Category '
                                                     + category.category_name + ' deleted'})), 200
        return make_response(jsonify({'message': 'Category not authenticated'})), 401


filtered_category = FilteredCategoryManipulations.as_view('filtered_category')
nonfiltered_category = NonFilteredCategoryManipulations.as_view('nonfiltered_category')
