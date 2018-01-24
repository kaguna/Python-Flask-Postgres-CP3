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

    def test_login_with_empty_fields(self):
        """Test API can login with empty fields
        """
        empty_login_details = {'email': '', 'password': ''}
        response = self.client().post('/auth/login', data=empty_login_details)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Please fill all the fields', str(response.data))

    def test_login_with_invalid_email(self):
        """Test API can login with invalid email.
        """
        invalid_email = {'email': 'jimgmail.com', 'password': 'Pass123'}
        response = self.client().post('/auth/login', data=invalid_email)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid email given', str(response.data))

    def test_login_with_short_password(self):
        """Test API can login with short password
        """
        short_password = {'email': 'jim@gmail.com', 'password': 'Pass'}
        response = self.client().post('/auth/login', data=short_password)
        self.assertEqual(response.status_code, 412)
        self.assertIn('The password is too short', str(response.data))

    def test_login_with_unregistered_user(self):
        """Test API can login with user not registered.
        """
        unregistered_email = {'email': 'jim@gmail.com', 'password': 'Pass123'}
        response = self.client().post('/auth/login', data=unregistered_email)
        self.assertEqual(response.status_code, 404)
        self.assertIn('User not registered!', str(response.data))

    def test_login_with_wrong_password(self):
        """Test API can login with wrong password.
        """
        wrong_password = {'email': 'kaguna@gmail.com', 'password': 'Jim1234'}
        response = self.client().post('/auth/login', data=wrong_password)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Wrong email or password.', str(response.data))

    def test_invalid_token(self):
        """Test invalid token
        """
        invalid_token = 'gfgf5654564fghfghutyiy8y78'
        res = self.client().post('auth/logout', headers={'x-access-token': invalid_token})
        self.assertEqual(res.status_code, 400)
        self.assertIn('Invalid access token.', str(res.data))

    # Test the send Request

    def test_send_token_on_invalid_email(self):
        """Test if the API can reject wrong email format provided
        """
        invalid_email = {'email': 'kagunagmail.com'}
        return_values = self.client().post('/auth/send_reset_password_token', data=invalid_email)
        self.assertEqual(return_values.status_code, 400)
        self.assertIn('Invalid email given', str(return_values.data))

    def test_send_token_to_empty_email_field(self):
        """Test send token on an empty email field.
        """
        empty_email_field = {'email': ''}
        return_values = self.client().post('/auth/send_reset_password_token', data=empty_email_field)
        self.assertEqual(return_values.status_code, 412)
        self.assertIn('Please fill all the fields', str(return_values.data))

    def test_send_token__to_unregistered_email(self):
        """Test API cannot send token to an unregistered user.
        """
        unregistered_email = {'email': 'jim@gmail.com'}
        response = self.client().post('/auth/send_reset_password_token', data=unregistered_email)
        self.assertEqual(response.status_code, 404)
        self.assertIn('User does not exist!', str(response.data))

