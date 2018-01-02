# This file will have all the categories CRUD operations tested

import unittest
import json
from app import create_app, db


class CategoriesTestCase(unittest.TestCase):
    """This class represents the categories test cases"""
    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client()
        self.register_user = {'email': 'jim@gmail.com', 'username': 'jim', 'password': 'pass123'}
        login_user = {"email": "jim@gmail.com", "password": "pass123"}
        self.categories = {'category_name': 'Lunch'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

        self.client.post('/auth/register', data=self.register_user)
        login_details = self.client.post('/auth/login', data=login_user)
        self.access_token = json.loads(login_details.data.decode())['access_token']

    """Test category creation(POST)
    """
    def test_category_creation(self):
        """Test API can create a category (POST request)
        """
        res = self.client.post('/categories', headers={'x-access-token': self.access_token}, data=self.categories)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Category created successfully', str(res.data))

    def test_category_existence(self):
        """Test if API can create a category (POST request) that exists
        """
        self.client.post('/categories', headers={'x-access-token': self.access_token}, data=self.categories)
        res = self.client.post('/categories', headers={'x-access-token': self.access_token}, data=self.categories)
        self.assertEqual(res.status_code, 409)
        self.assertIn('Category exists!', str(res.data))

    def test_invalid_category_name(self):
        """Test if API can create a category with an invalid name
        """
        categories = {'category_name': '$%#%^&&'}
        res = self.client.post('/categories', headers={'x-access-token': self.access_token}, data=categories)
        self.assertEqual(res.status_code, 400)
        self.assertIn('Invalid category name given', str(res.data))

    def test_empty_category_name(self):
        """Test if API can create a category with name not provided
        """
        self.categories = {'category_name': ''}
        res = self.client.post('/categories', headers={'x-access-token': self.access_token}, data=self.categories)
        self.assertEqual(res.status_code, 422)
        self.assertIn('Please fill all the fields', str(res.data))

    """Test category name update(PUT)
    """
    def test_category_update(self):
        """Test API can update a category (PUT request)
        """
        self.client.post('/categories', headers={'x-access-token': self.access_token}, data=self.categories)
        new_category_name = {'category_name': 'Breakfast'}
        res = self.client.put('/category/1', headers={'x-access-token': self.access_token}, data=new_category_name)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Category updated successfully', str(res.data))

    def test_category_update_existence(self):
        """Test if API can update a category (PUT request) that exists
        """
        self.client.post('/categories', headers={'x-access-token': self.access_token}, data=self.categories)
        self.client.put('/category/1', headers={'x-access-token': self.access_token}, data=self.categories)
        res = self.client.post('/categories', headers={'x-access-token': self.access_token}, data=self.categories)
        self.assertEqual(res.status_code, 409)
        self.assertIn('Category exists!', str(res.data))

    def test_invalid_update_category_name(self):
        """Test if API can update a category with an invalid name
        """
        self.client.post('/categories', headers={'x-access-token': self.access_token}, data=self.categories)
        categories = {'category_name': '$%#%^&&'}
        res = self.client.put('/category/1', headers={'x-access-token': self.access_token}, data=categories)
        self.assertEqual(res.status_code, 400)
        self.assertIn('Invalid category name given', str(res.data))

    def test_update_non_existence_category(self):
        """Test API can update a category which does not exist (UPDATE request)
        """
        self.client.post('/categories', headers={'x-access-token': self.access_token}, data=self.categories)
        res = self.client.delete('/category/3', headers={'x-access-token': self.access_token}, data=self.categories)
        self.assertEqual(res.status_code, 401)
        self.assertIn('Category not found', str(res.data))

    def test_empty_update_category_name(self):
        """Test if API can update a category with name not provided
        """
        self.client.post('/categories', headers={'x-access-token': self.access_token}, data=self.categories)
        self.categories = {'category_name': ''}
        res = self.client.put('/category/1', headers={'x-access-token': self.access_token}, data=self.categories)
        self.assertEqual(res.status_code, 422)
        self.assertIn('Please fill all the fields', str(res.data))

    """Test category deletion
    """

    def test_category_deletion(self):
        """Test API can delete a category (DELETE request)
        """
        self.client.post('/categories', headers={'x-access-token': self.access_token}, data=self.categories)
        res = self.client.delete('/category/1', headers={'x-access-token': self.access_token}, data=self.categories)
        self.assertEqual(res.status_code, 200)
        self.assertIn('Category deleted', str(res.data))

    def test_delete_non_existence_category(self):
        """Test API can delete a category which does not exist (DELETE request)
        """
        self.client.post('/categories', headers={'x-access-token': self.access_token}, data=self.categories)
        res = self.client.delete('/category/3', headers={'x-access-token': self.access_token}, data=self.categories)
        self.assertEqual(res.status_code, 401)
        self.assertIn('Category not found', str(res.data))

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

    # Make the tests conveniently executable
    if __name__ == "__main__":
        unittest.main()
