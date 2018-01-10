# This file will have all the recipes CRUD operations tested

import unittest
import json
from app import create_app, db


class RecipesTestCase(unittest.TestCase):
    """This class represents the recipes test cases"""
    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client()
        self.register_user = {'email': 'jim@gmail.com', 'username': 'jim', 'password': 'pass123'}
        login_user = {"email": "jim@gmail.com", "password": "pass123"}
        self.category = {"category_name": "Lunch"}
        self.recipes = {"recipe_name": "Ugali", "recipe_procedure": "Boil the water put flour and mix."}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

        self.client.post('/auth/register', data=self.register_user)
        login_details = self.client.post('/auth/login', data=login_user)
        self.access_token = json.loads(login_details.data.decode())['access_token']
        self.client.post('/categories/', headers={'x-access-token': self.access_token}, data=self.category)

    """Test recipe creation(POST)
    """
    def test_recipe_creation(self):
        """Test API can create a recipe (POST request)
        """
        response = self.client.post('/category/1/recipes/', headers={'x-access-token': self.access_token},
                                    data=self.recipes)
        self.assertEqual(response.status_code, 201)
        self.assertIn('Recipe created successfully', str(response.data))

    def test_empty_recipe_field(self):
        """Test if the the recipe registration will be successful when any form field is empty
        """
        recipes = {"recipe_name": "", "recipe_procedure": "Boil the water put flour and mix."}
        response = self.client.post('/category/1/recipes/', headers={'x-access-token': self.access_token},
                                    data=recipes)
        self.assertEqual(response.status_code, 422)
        self.assertIn('Please fill all the fields', str(response.data))

    def test_invalid_recipe_name(self):
        """Test if the the recipe registration will be successful when recipe name is invalid
        """
        recipes = {"recipe_name": "!@#$$%^&*", "recipe_procedure": "Boil the water put flour and mix."}
        response = self.client.post('/category/1/recipes/', headers={'x-access-token': self.access_token},
                                    data=recipes)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid recipe name or procedure given', str(response.data))

    def test_duplicate_recipe(self):
        """Test if the the recipe registration will be successful when recipe is already registered
        """
        self.client.post('/category/1/recipes/', headers={'x-access-token': self.access_token},
                         data=self.recipes)
        response = self.client.post('/category/1/recipes/', headers={'x-access-token': self.access_token},
                                    data=self.recipes)
        self.assertEqual(response.status_code, 409)
        self.assertIn('Recipe exists!', str(response.data))

    def test_with_non_existing_category(self):
        """Test if the the recipe registration will be successful when category does not exist.
        """
        response = self.client.post('/category/5/recipes/', headers={'x-access-token': self.access_token},
                                    data=self.recipes)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Category not found', str(response.data))

    """Test recipe get specific recipe(GET)
    """

    def test_get_specific_recipe(self):
        """Test retrieving a specific recipe
        """
        self.client.post('/category/1/recipes/', headers={'x-access-token': self.access_token},
                         data=self.recipes)
        response = self.client.get('/category/1/recipe/1', headers={'x-access-token': self.access_token},
                                   data=self.recipes)
        self.assertEqual(response.status_code, 200)

    def test_get_non_existing_recipe(self):
        """Test retrieving a recipe not yet registered
        """
        response = self.client.get('/category/1/recipe/1', headers={'x-access-token': self.access_token},
                                   data=self.recipes)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Recipe not found', str(response.data))

    """Test editing specific recipe(PUT)
    """

    def test_recipe_successful_editing(self):
        """Test API can edit an existing recipe
        """
        self.client.post('/category/1/recipes/', headers={'x-access-token': self.access_token},
                         data=self.recipes)
        response = self.client.put('/category/1/recipe/1', headers={'x-access-token': self.access_token},
                                   data={"recipe_name": "Sembe",
                                         "recipe_procedure": "Boil the water put flour and mix."})
        self.assertEqual(response.status_code, 201)
        self.assertIn('Recipe updated successfully', str(response.data))

    def test_editing_with_empty_recipe_field(self):
        """Test if the the recipe editing will be successful when any form field is empty
        """
        self.client.post('/category/1/recipes/', headers={'x-access-token': self.access_token},
                         data=self.recipes)
        recipes = {"recipe_name": "", "recipe_procedure": "Boil the water put flour and mix."}
        response = self.client.put('/category/1/recipe/1', headers={'x-access-token': self.access_token},
                                   data=recipes)
        self.assertEqual(response.status_code, 422)
        self.assertIn('Please fill all the fields', str(response.data))

    def test_editng_with_invalid_recipe_name(self):
        """Test if the the recipe editing will be successful when recipe name is invalid
        """
        self.client.post('/category/1/recipes/', headers={'x-access-token': self.access_token},
                         data=self.recipes)
        recipes = {"recipe_name": "!@#$$%^&*", "recipe_procedure": "Boil the water put flour and mix."}
        response = self.client.put('/category/1/recipe/1', headers={'x-access-token': self.access_token},
                                   data=recipes)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid recipe name given', str(response.data))

    def test_editing_with_existing_recipe(self):
        """Test if the the recipe editing will be successful when recipe is already registered
        """
        self.client.post('/category/1/recipes/', headers={'x-access-token': self.access_token},
                         data=self.recipes)
        self.client.post('/category/1/recipes/', headers={'x-access-token': self.access_token},
                         data=self.recipes)
        response = self.client.put('/category/1/recipe/1', headers={'x-access-token': self.access_token},
                                   data=self.recipes)
        self.assertEqual(response.status_code, 409)
        self.assertIn('Recipe exists!', str(response.data))

    def test_editing_with_non_existing_recipe(self):
        """Test if the the recipe editing will be successful when recipe does not exist.
        """
        self.client.post('/category/1/recipes/', headers={'x-access-token': self.access_token},
                         data=self.recipes)
        response = self.client.put('/category/5/recipe/1', headers={'x-access-token': self.access_token},
                                   data=self.recipes)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Recipe not found', str(response.data))

    """Test deleting specific recipe(DELETE)
    """

    def test_recipe_successful_deletion(self):
        """Test API can delete a recipe
        """
        self.client.post('/category/1/recipes/', headers={'x-access-token': self.access_token},
                         data=self.recipes)
        response = self.client.delete('/category/1/recipe/1', headers={'x-access-token': self.access_token},
                                      data=self.recipes)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Recipe deleted', str(response.data))

    def test_deleting_non_existing_recipe(self):
        """Test deleting non existing recipe
        """
        response = self.client.delete('/category/1/recipe/1', headers={'x-access-token': self.access_token},
                                      data=self.recipes)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Recipe not found', str(response.data))

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

    # Make the tests conveniently executable
    if __name__ == "__main__":
        unittest.main()
