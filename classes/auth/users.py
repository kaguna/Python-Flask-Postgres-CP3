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
        user_email = str(request.data.get('email', ''))
        user_name = str(request.data.get('username', ''))
        user_password = str(request.data.get('password', ''))
        if user_email and user_name and user_password:
            if re.search(email_pattern, user_email):
                if len(user_password) >= 7:

                    user_creation = Users(email=user_email, username=user_name,
                                          password=user_password)
                    user_creation.save()
                    # 412-error: pre-conditions specified did not hold.
                    return make_response(jsonify({'message': 'User created successfully'})), 201
                return make_response(jsonify({'message': 'The password is too short'})), 412
            return make_response(jsonify({'message': 'Invalid email given'})), 412
        return make_response(jsonify({'message': 'Please fill all the fields'})), 412


"""Link the class and operation to a variable."""
user_creation = CreateUser.as_view('user_creation')
