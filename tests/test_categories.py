# This file will have all the categories CRUD operations tested

from .base_tests import BaseTestCase
import json


class CategoriesTestCase(BaseTestCase):
    """This class represents the categories test cases"""

    def setUp(self):
        super(CategoriesTestCase, self).setUp()
        self.client().post('/auth/register', data=self.register_user)
        login_details = self.client().post('/auth/login', data=self.login_user)
        self.access_token = json.loads(login_details.data.decode())['access_token']
        self.res = self.client().post('/categories/', headers={'x-access-token': self.access_token},
                                      data=self.categories)

    # Test category creation(POST)

    def test_success_category_creation(self):
        """Test API can create a category (POST request)
        """
        self.assertEqual(self.res.status_code, 201)
        self.assertIn('Category created successfully', str(self.res.data))

    def test_creation_with_existing_category(self):
        """Test if API can create a category (POST request) that exists
        """
        res = self.client().post('/categories/', headers={'x-access-token': self.access_token},
                                 data=self.categories)
        self.assertEqual(res.status_code, 409)
        self.assertIn('Category exists!', str(res.data))

    def test_invalid_category_name(self):
        """Test if API can create a category with an invalid name
        """
        categories = {'category_name': '$%#%^&&'}
        res = self.client().post('/categories/', headers={'x-access-token': self.access_token},
                                 data=categories)
        self.assertEqual(res.status_code, 400)
        self.assertIn('Invalid category name given', str(res.data))

    def test_creation_with_empty_category_name(self):
        """Test if API can create a category with name not provided
        """
        categories = {'category_name': ''}
        res = self.client().post('/categories/', headers={'x-access-token': self.access_token},
                           data=categories)
        self.assertEqual(res.status_code, 400)
        self.assertIn('Please fill all the fields', str(res.data))

    # Test category name update(PUT)

    def test_successful_category_name_update(self):
        """Test API can edit a category name (PUT request)
        """
        new_category_name = {'category_name': 'Breakfast'}
        res = self.client().put('/category/1', headers={'x-access-token': self.access_token},
                                data=new_category_name)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Category updated successfully', str(res.data))

    def test_update_with_existing_category_name(self):
        """Test if API can update a category (PUT request) that exists
        """
        self.client().put('/category/1', headers={'x-access-token': self.access_token},
                          data=self.categories)
        res = self.client().post('/categories/', headers={'x-access-token': self.access_token},
                               data=self.categories)
        self.assertEqual(res.status_code, 409)
        self.assertIn('Category exists!', str(res.data))

    def test_update_with_invalid_category_name(self):
        """Test if API can update a category with an invalid name
        """
        categories = {'category_name': '$%#%^&&'}
        res = self.client().put('/category/1', headers={'x-access-token': self.access_token},
                                data=categories)
        self.assertEqual(res.status_code, 400)
        self.assertIn('Invalid category name given', str(res.data))

    def test_update_non_existing_category(self):
        """Test API can update a category which does not exist (UPDATE request)
        """
        res = self.client().put('/category/3', headers={'x-access-token': self.access_token},
                                   data=self.categories)
        self.assertEqual(res.status_code, 401)
        self.assertIn('Category does not exist.', str(res.data))

    def test_update_with_empty_category_name(self):
        """Test if API can update a category with name not provided
        """
        self.categories = {'category_name': ''}
        res = self.client().put('/category/1', headers={'x-access-token': self.access_token},
                                data=self.categories)
        self.assertEqual(res.status_code, 400)
        self.assertIn('Please fill all the fields', str(res.data))

    # Test category deletion

    def test_successful_category_deletion(self):
        """Test API can delete a category (DELETE request)
        """
        res = self.client().delete('/category/1', headers={'x-access-token': self.access_token},
                                   data=self.categories)
        self.assertEqual(res.status_code, 200)
        self.assertIn('Category deleted successfully', str(res.data))

    def test_deleting_non_existing_category(self):
        """Test API can delete a category which does not exist (DELETE request)
        """
        res = self.client().delete('/category/3', headers={'x-access-token': self.access_token},
                                   data=self.categories)
        self.assertEqual(res.status_code, 401)
        self.assertIn('Category does not exist.', str(res.data))

    # Test category retrieval

    def test_get_category_with_invalid_page(self):
        """Test API can retrieve a category on a non existing page.
        """
        res = self.client().get('/category/?page=105', headers={'x-access-token': self.access_token})
        self.assertEqual(res.status_code, 404)

    def test_retrieve_non_existing_category_by_search(self):
        """Test retrieving a non existing category by searching
        """
        response = self.client().get('/categories/?q=Breako', headers={'x-access-token': self.access_token})
        self.assertIn("Category does not exist.", str(response.data))
        self.assertEqual(response.status_code, 401)

    def test_retrieve_non_existing_category(self):
        """Test API can retrieve a non existing category.
        """
        res = self.client().get('/category/4', headers={'x-access-token': self.access_token},
                                data=self.categories)
        self.assertEqual(res.status_code, 401)
        self.assertIn('Category does not exist.', str(res.data))

    def test_retrieve_specific_category(self):
        """Test API can retrieve a specific category.
        """
        res = self.client().get('/category/1', headers={'x-access-token': self.access_token},
                                data=self.categories)
        self.assertEqual(res.status_code, 200)
