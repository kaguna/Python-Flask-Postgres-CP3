# This file will create the user and reset the password.
import re
from flask import request, jsonify, make_response
from app.models import Users
from flask.views import MethodView


class CreateUser(MethodView):
    """This class will handle the creation of new users
    """
    email_pattern = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    regex_username = "^[a-zA-Z0-9-+\s]{4,20}$"

    @classmethod
    def post(self):
        # create user using post method
        """
        Register user
        ---
        tags:
          - Authentication
        parameters:
          - in: body
            name: user details
            description: User's email, username and password
            type: string
            required: true
            schema:
              id: register
              properties:
                email:
                  default: jimmy@gmail.com
                username:
                  default: kaguna
                password:
                  default: pass1234
        responses:
          201:
            description: User registered successfully
          409:
            description: User exists!
          400:
            description: Invalid email or username given
          412:
            description: The password is too short
          422:
            description: Please fill all the fields
        """
        user_email = str(request.data.get('email', '')).strip().lower()
        user = Users.query.filter_by(email=user_email).first()
        user_name = str(request.data.get('username', '')).strip()
        user_password = str(request.data.get('password', ''))

        if not user_email and not user_name and not user_password:
            return make_response(jsonify({'message': 'Please fill all the fields'})), 400

        if not re.search(self.email_pattern, user_email):
            return make_response(jsonify({'message': 'Invalid email given'})), 400

        if not re.search(self.regex_username, user_name):
            return make_response(jsonify({'message': 'Invalid username given'})), 400

        if len(user_password) < 7:
            return make_response(jsonify({'message': 'The password is too short'})), 412

        if user:
            return make_response(jsonify({'message': 'User exists!'})), 409

        user_creation = Users(email=user_email, username=user_name, password=user_password)
        user_creation.save()
        return make_response(jsonify({'message': 'User registered successfully'})), 201


class ResetPassword(MethodView):
    """This class will handle the resetting of password"""
    @classmethod
    def put(self):
        # This method will edit the already existing password

        """
        Reset password
        ---
        tags:
          - Authentication
        parameters:
          - in: body
            name: user details
            description: User's email, password and re-typed password
            type: string
            required: true
            schema:
              id: password_reset
              properties:
                email:
                  default: jimmy@gmail.com
                retyped_password:
                  default: pass1234
                password:
                  default: pass1234
        responses:
          201:
            description: Password resetting is successful
          409:
            description: User exists!
          400:
            description: Invalid email given
          404:
            description: User does not exist!
          412:
            description: The password is too short
          422:
            description: Please fill all the fields
        """
        user_email = str(request.data.get('email', '')).strip().lower()
        user_password = str(request.data.get('password', ''))
        retyped_password = str(request.data.get('retyped_password', ''))
        user = Users.query.filter_by(email=user_email).first()

        if not user_email and not user_password:
            return make_response(jsonify({'message': 'Please fill all the fields'})), 400

        if not re.search(CreateUser.email_pattern, user_email):
            return make_response(jsonify({'message': 'Invalid email given'})), 400

        if len(user_password) < 7 and  len(retyped_password) < 7:
            return make_response(jsonify({'message': 'The password is too short'})), 412

        if user_password != retyped_password:
            return make_response(jsonify({'message': 'Password mismatch'})), 400

        if not user:
            return make_response(jsonify({'message': 'User does not exist!'})), 404

        user.password = user_password
        user.save()
        return make_response(jsonify({'message': 'Password resetting is successful'})), 201


# Link the class and operation to a variable.
user_creation = CreateUser.as_view('user_creation')
reset_password = ResetPassword.as_view('reset_password')
