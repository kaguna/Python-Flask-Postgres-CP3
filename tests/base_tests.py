# This file will provide the base for the most used functions and variables

import unittest
from app import create_app, db


class BaseTestCase(unittest.TestCase):
        def setUp(self):
            super(BaseTestCase, self).setUp()
            # Define test variables and initialize app.
            self.app = create_app("testing")
            self.app_context = self.app.app_context()
            self.app_context.push()
            self.client = self.app.test_client
            self.register_user = {'email': 'kaguna@gmail.com', 'username': 'james', 'password': 'james123'}
            self.login_user = {"email": "kaguna@gmail.com", "password": "james123"}

            self.categories = {'category_name': 'Lunch'}
            self.recipes = {"recipe_name": "Ugali",
                            "recipe_procedure": "Boil the water put flour and mix."}

            # binds the app to the current context
            with self.app_context:
                # create all tables
                db.create_all()

        def tearDown(self):
            """teardown all initialized variables."""
                # drop all tables
            db.session.remove()
            db.drop_all()
