# Authenticate all other files using the existing token from this file

from flask import request, jsonify
import os
import jwt
from functools import wraps


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        access_token = None
        access_token = request.headers.get('x-access-token')
        if not access_token:
            return jsonify({'messgae': 'Token is missing.'}), 401
        try:
            data = jwt.decode(access_token, os.getenv('SECRET'))
            user_in_session = data['id']
        except:
            return jsonify({'messgae': 'Token is invalid.'}), 401

        return f(user_in_session, *args, **kwargs)
    return decorated
