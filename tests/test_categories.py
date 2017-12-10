# This file will have all the categories CRUD operations tested

import unittest
import os
from app import create_app, db


class CategoriesTestCase(unittest.TestCase):
    """This class represents the categories test cases"""
    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.categories = {'category_name': 'Lunch'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def test_category_creation(self):
        """Test API can create a category (POST request)"""
        res = self.client().post('/categories/', data=self.categories)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Lunch', str(res.data))

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

    # Make the tests conveniently executable
    if __name__ == "__main__":
        unittest.main()
