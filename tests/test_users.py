# This file tests user authentication
from .base_tests import BaseTestCase
import json


class UsersAuthTestCase(BaseTestCase):
    """This class represents the users auth test cases
    """

    def setUp(self):
        super(UsersAuthTestCase, self).setUp()
        self.register_response = self.client().post('/auth/register', data=self.register_user)
        self.login_details = self.client().post('/auth/login', data=self.login_user)
        self.access_token = json.loads(self.login_details.data.decode())['access_token']

    # User creation

    def test_successful_user_creation(self):
        """Test API can create a user (POST request)"""
        self.assertEqual(self.register_response.status_code, 201)
        self.assertIn('User registered successfully', str(self.register_response.data))

    def test_invalid_email(self):
        """Test if the API can reject wrong email format provided
        """
        invalid_email = {'email': 'kagunagmail.com', 'username': 'kaguna', 'password': 'james123'}
        return_values = self.client().post('/auth/register', data=invalid_email)
        self.assertEqual(return_values.status_code, 400)
        self.assertIn('Invalid email given', str(return_values.data))

    def test_invalid_username(self):
        """Test if the API can reject wrong username format provided
        """
        invalid_username = {'email': 'kaguna@gmail.com', 'username': '@@##$%', 'password': 'james123'}
        return_values = self.client().post('/auth/register', data=invalid_username)
        self.assertEqual(return_values.status_code, 400)
        self.assertIn('Invalid username given', str(return_values.data))

    def test_on_empty_fields_submission(self):
        """Test if the API can reject empty fields
        """
        empty_fields = {'email': '', 'username': '', 'password': ''}
        return_values = self.client().post('/auth/register', data=empty_fields)
        self.assertEqual(return_values.status_code, 400)
        self.assertIn('Please fill all the fields', str(return_values.data))

    def test_length_of_password(self):
        """Test if the API can reject a password with less than 7 characters
        """
        password_length = {'email': 'kaguna@gmail.com', 'username': 'james', 'password': 'j123'}
        return_values = self.client().post('/auth/register', data=password_length)
        self.assertEqual(return_values.status_code, 412)
        self.assertIn('The password is too short', str(return_values.data))

    def test_with_user_email_already_created(self):
        """Test if the API can reject a user who exists in the database
        """
        return_values = self.client().post('/auth/register', data=self.register_user)
        self.assertEqual(return_values.status_code, 409)
        self.assertIn('User exists!', str(return_values.data))

    # User reset password

    def test_successful_user_reset_password(self):
        """Test API can reset password
        """
        new_password_details = {'email': 'kaguna@gmail.com', 'password': 'james123',
                                'retyped_password': 'james123'}
        response = self.client().put('/auth/reset_password',
                                     headers={'x-access-token': self.access_token},
                                     data=new_password_details)
        self.assertEqual(response.status_code, 201)
        self.assertIn('Password resetting is successful', str(response.data))

    def test_reset_password_with_invalid_email(self):
        """Test API can reset password with invalid email
        """
        new_password_details = {'email': 'kagunagmail.com', 'password': 'james123',
                                'retyped_password': 'james123'}
        response = self.client().put('/auth/reset_password',
                                     headers={'x-access-token': self.access_token},
                                     data=new_password_details)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid email given', str(response.data))

    def test_reset_password_with_short_password(self):
        """Test API can reset password with short password
        """
        new_password_details = {'email': 'kaguna@gmail.com', 'password': 'jam',
                                'retyped_password': 'jam'}
        response = self.client().put('/auth/reset_password',
                                     headers={'x-access-token': self.access_token},
                                     data=new_password_details)
        self.assertEqual(response.status_code, 412)
        self.assertIn('The password is too short', str(response.data))

    def test_reset_password_with_password_mismatch(self):
        """Test API can reset password with password mismatch
        """
        new_password_details = {'email': 'kaguna@gmail.com', 'password': 'james123',
                                'retyped_password': 'james321'}
        response = self.client().put('/auth/reset_password',
                                     headers={'x-access-token': self.access_token},
                                     data=new_password_details)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Password mismatch', str(response.data))

    # Test login

    def test_successful_login(self):
        """Test API can successfully login.
        """
        self.assertEqual(self.login_details.status_code, 200)
        self.assertIn('Successful login', str(self.login_details.data))


