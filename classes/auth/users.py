# This file will create the user.
import re
from flask import request, jsonify, make_response
from app.models import Users
from flask.views import MethodView


class CreateUser(MethodView):
    """This class will handle the creation of new users"""

    def post(self):
        # create user using post method
        email_pattern = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        user_email = str(request.data.get('email', '')).strip()
        user = Users.query.filter_by(email=user_email).first()
        user_name = str(request.data.get('username', '')).strip()
        user_password = str(request.data.get('password', ''))
        if user_email and user_name and user_password:
            if re.search(email_pattern, user_email):
                if len(user_password) >= 7:
                    if not user:

                        user_creation = Users(email=user_email, username=user_name, password=user_password)
                        user_creation.save()

                        return make_response(jsonify({'message': 'User registered successfully'})), 201
                    return make_response(jsonify({'message': 'User exists!'})), 409
                return make_response(jsonify({'message': 'The password is too short'})), 412
            return make_response(jsonify({'message': 'Invalid email given'})), 400
        return make_response(jsonify({'message': 'Please fill all the fields'})), 422


"""Link the class and operation to a variable."""
user_creation = CreateUser.as_view('user_creation')
