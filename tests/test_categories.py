# This file will have all the categories CRUD operations tested

import unittest
import json
from app import create_app, db
from flask import request


class CategoriesTestCase(unittest.TestCase):
    """This class represents the categories test cases"""
    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.register_user = {'email': 'jim@gmail.com', 'username': 'jim', 'password': 'pass123'}
        self.login_user= {'email': 'jim@gmail.com', 'password': 'pass123'}
        self.categories = {'category_name': 'Lunch'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

        self.client().post('auth/user/', data=self.register_user)
        self.login_details = self.client().post('auth/login/', data=self.login_user)
        self.access_token = json.loads(self.login_details.data.decode())['access_token']

    def define_header(self, access_token):
        access_token = request.headers.get('x-access-token')
        return access_token

    def test_category_creation(self):
        """Test API can create a category (POST request)"""
        res = self.client().post('/categories/',headers ={'x-access-token':self.access_token}, data=self.categories)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Category created successfully', str(res.data))

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

    # Make the tests conveniently executable
    if __name__ == "__main__":
        unittest.main()
