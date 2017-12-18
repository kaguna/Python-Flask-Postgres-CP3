# This file will authenticate the user upon login.
import re
import os
from flask import request, jsonify, make_response
from app.models import Users
from flask.views import MethodView
import jwt
import datetime


class UserLoginAuthentication(MethodView):
    """This class will handle the access of resources by user through login.
    """

    def post(self):
        # User login using post method
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
                                                  os.getenv('SECRET'))
                        if access_token:

                            valid_response = {'access_token': access_token.decode('UTF-8'),
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


"""Link the class and operation to a variable."""
user_login = UserLoginAuthentication.as_view('user_login')
