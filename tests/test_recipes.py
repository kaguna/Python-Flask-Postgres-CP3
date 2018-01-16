# This file will have all the recipes CRUD operations tested

import json
from .base_tests import BaseTestCase


class RecipesTestCase(BaseTestCase):
    """This class represents the recipes test cases"""
    def setUp(self):
        super(RecipesTestCase, self).setUp()
        self.client().post('/auth/register', data=self.register_user)
        login_details = self.client().post('/auth/login', data=self.login_user)
        self.access_token = json.loads(login_details.data.decode())['access_token']
        self.client().post('/categories/', headers={'x-access-token': self.access_token}, data=self.categories)
        self.response = self.client().post('/category/1/recipes/', headers={'x-access-token': self.access_token},
                                      data=self.recipes)

    # Test recipe creation(POST)

    def test_successful_recipe_creation(self):
        """Test API can create a recipe (POST request)
        """
        self.assertEqual(self.response.status_code, 201)
        self.assertIn('Recipe created successfully', str(self.response.data))

    def test_recipe_creation_with_empty_recipe_fields(self):
        """Test if the the recipe registration will be successful when any form field is empty
        """
        recipes = {"recipe_name": "", "recipe_procedure": ""}
        response = self.client().post('/category/1/recipes/', headers={'x-access-token': self.access_token},
                                      data=recipes)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Please fill all the fields', str(response.data))

    def test_creation_with_invalid_recipe_name(self):
        """Test if the the recipe registration will be successful when recipe name is invalid
        """
        recipes = {"recipe_name": "!@#$$%^&*", "recipe_procedure": "Boil the water put flour and mix."}
        response = self.client().post('/category/1/recipes/', headers={'x-access-token': self.access_token},
                                      data=recipes)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid recipe name given', str(response.data))

    def test_recipe_creation_with_existing_recipe_name(self):
        """Test if the the recipe registration will be successful when recipe is already registered
        """
        response = self.client().post('/category/1/recipes/', headers={'x-access-token': self.access_token},
                                      data=self.recipes)
        self.assertEqual(response.status_code, 409)
        self.assertIn('Recipe name exists!', str(response.data))

    def test_recipe_creation_with_non_existing_category(self):
        """Test if the the recipe registration will be successful when category does not exist.
        """
        response = self.client().post('/category/5/recipes/', headers={'x-access-token': self.access_token},
                                      data=self.recipes)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Category does not exist.', str(response.data))

    # Test recipe get specific recipe(GET)

    def test_retrieve_specific_recipe_with_id(self):
        """Test retrieving a specific recipe
        """
        response = self.client().get('/category/1/recipe/1', headers={'x-access-token': self.access_token},
                                     data=self.recipes)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_non_existing_recipe(self):
        """Test retrieving a recipe not yet registered
        """
        response = self.client().get('/category/1/recipe/5', headers={'x-access-token': self.access_token},
                                     data=self.recipes)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Recipe does not exist', str(response.data))

    def test_retrieve_specific_recipe_by_search(self):
        """Test retrieving a specific recipe by searching
        """
        response = self.client().get('/category/1/recipes/?q=Ugali', headers={'x-access-token': self.access_token})
        self.assertIn("Ugali", str(response.data))
        self.assertEqual(response.status_code, 200)

    def test_retrieve_non_existing_recipe_by_search(self):
        """Test retrieving a non existing recipe by searching
        """
        response = self.client().get('/category/1/recipes/?q=sembe', headers={'x-access-token': self.access_token})
        self.assertIn("Recipe does not exist.", str(response.data))
        self.assertEqual(response.status_code, 404)

    # Test updating specific recipe(PUT)

    def test_successful_recipe_name_update(self):
        """Test API can update an existing recipe
        """
        response = self.client().put('/category/1/recipe/1', headers={'x-access-token': self.access_token},
                                     data={"recipe_name": "Sembe",
                                           "recipe_procedure": "Boil the water put flour and mix."})
        self.assertEqual(response.status_code, 201)
        self.assertIn('Recipe updated successfully', str(response.data))

    def test_update_with_empty_recipe_fields(self):
        """Test if the the recipe updating will be successful when any form field is empty
        """
        empty_recipe_name = {"recipe_name": " ", "recipe_procedure": " "}
        response = self.client().put('/category/1/recipe/1', headers={'x-access-token': self.access_token},
                                     data=empty_recipe_name)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Please fill all the fields', str(response.data))

    def test_update_with_invalid_recipe_name(self):
        """Test if the the recipe updating will be successful when recipe name is invalid
        """
        recipes = {"recipe_name": "!@#$$%^&*", "recipe_procedure": "Boil the water put flour and mix."}
        response = self.client().put('/category/1/recipe/1', headers={'x-access-token': self.access_token},
                                     data=recipes)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid recipe name given', str(response.data))

    def test_update_with_existing_recipe_name(self):
        """Test if the the recipe updating will be successful when recipe is already registered
        """
        response = self.client().put('/category/1/recipe/1', headers={'x-access-token': self.access_token},
                                     data=self.recipes)
        self.assertEqual(response.status_code, 409)
        self.assertIn('Recipe name exists!', str(response.data))

    def test_update_recipe_name_within_different_category(self):
        """Test if the the recipe updating will be successful when recipe does not exist.
        """
        response = self.client().put('/category/5/recipe/1', headers={'x-access-token': self.access_token},
                                     data=self.recipes)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Recipe does not exist.', str(response.data))

    # Test deleting specific recipe(DELETE)

    def test_successful_recipe_deletion(self):
        """Test API can delete a recipe
        """
        response = self.client().delete('/category/1/recipe/1', headers={'x-access-token': self.access_token},
                                        data=self.recipes)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Recipe deleted', str(response.data))

    def test_deleting_non_existing_recipe(self):
        """Test deleting non existing recipe
        """
        response = self.client().delete('/category/1/recipe/5', headers={'x-access-token': self.access_token},
                                        data=self.recipes)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Recipe does not exist.', str(response.data))
