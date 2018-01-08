# Authenticate all other files using the existing token from this file

from flask import request, jsonify, make_response
import os
import jwt
from functools import wraps
from app.models import BlacklistToken


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        access_token = None
        access_token = request.headers.get('x-access-token')
        check_token = BlacklistToken.query.filter_by(token=access_token).first()

        if not access_token:
            return jsonify({'messgae': 'Token is missing.'}), 401

        if not check_token:
            try:
                data = jwt.decode(access_token, os.getenv('SECRET', '$#%^%$^%@@@@@56634@@@'))
                user_in_session = data['id']
            except Exception:
                return jsonify({'messgae': 'Token is invalid.'}), 401

            return f(user_in_session, *args, **kwargs)
        return make_response(jsonify({'message': 'The user is already logged out!'})), 409
    return decorated
