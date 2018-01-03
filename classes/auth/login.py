# This file will authenticate the user upon login.
import re
import os
from flask import request, jsonify, make_response
from app.models import Users
from flask.views import MethodView
import jwt
import datetime
from app.models import BlacklistToken


class UserLoginAuthentication(MethodView):
    """This class will handle the access of resources by user through login.
    """
    def post(self):
        # User login using post method
        """
        User login
        ---
        tags:
          - Authentication
        parameters:
          - in: body
            name: user details
            description: User's email and password
            type: string
            required: true
            schema:
              id: login
              properties:
                email:
                  default: jimmy@gmail.com
                password:
                  default: pass1234
        responses:
          201:
            description: Login Successful
          400:
            description: Bad request
        """
        email_pattern = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        user_email = str(request.data.get('email', '')).strip()
        user_password = str(request.data.get('password', ''))
        if user_email and user_password:
            if re.search(email_pattern, user_email):
                if len(user_password) >= 7:
                    user = Users.query.filter_by(email=user_email, password=user_password).first()
                    if user:
                        access_token = jwt.encode({'id': user.id,
                                                   'expiry_time': str(datetime.datetime.utcnow() +
                                                                      datetime.timedelta(minutes=30))},
                                                  os.getenv('SECRET', '$#%^%$^%@@@@@56634@@@'))
                        if access_token:

                            valid_response = {'access_token': access_token.decode(),
                                              'message': 'Successful login'
                                              }
                            return make_response(jsonify(valid_response)), 200

                        invalid_response = {'message': 'Invalid access token'
                                            }
                        return make_response(jsonify(invalid_response)), 401

                    return make_response(jsonify({'message': 'Invalid email or password!'})), 404
                return make_response(jsonify({'message': 'The password is too short'})), 412
            return make_response(jsonify({'message': 'Invalid email given'})), 400
        return make_response(jsonify({'message': 'Please fill all the fields'})), 422


class UserLogoutAuthentication(MethodView):
    """This will enable user to destroy the session of the current user.
    """

    def post(self):
        """Method to logout the user"""
        access_token = request.headers.get('x-access-token')
        if access_token:
            check_token = BlacklistToken.query.filter_by(token=access_token).first()
            if not check_token:
                save_tokens = BlacklistToken(token=access_token)
                save_tokens.save()

                return make_response(jsonify({'message': 'User logged out successfully'})), 200
            return make_response(jsonify({'message': 'The user is already logged out!'})), 409
        return make_response(jsonify({'message': 'Invalid access token'})), 401


"""Link the class and operation to a variable."""
user_login = UserLoginAuthentication.as_view('user_login')
user_logout = UserLogoutAuthentication.as_view('user_logout')
