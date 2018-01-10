# This file tests user authentication
import unittest
from app import create_app, db


class UsersAuthTestCase(unittest.TestCase):
    """This class represents the users auth test cases"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.users = {'email': 'kaguna@gmail.com', 'username': 'james', 'password': 'james123'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    """ User creation"""
    def test_successful_user_registration(self):
        """Test API can create a user (POST request)"""
        return_values = self.client().post('/auth/register', data=self.users)
        self.assertEqual(return_values.status_code, 201)
        self.assertIn('User registered successfully', str(return_values.data))

    def test_invalid_email(self):
        """Test if the API can reject wrong email format provided
        """
        invalid_email = {'email': 'kagunagmail.com', 'username': '@@##$%', 'password': 'james123'}
        return_values = self.client().post('/auth/register', data=invalid_email)
        self.assertEqual(return_values.status_code, 400)
        self.assertIn('Invalid email or username given', str(return_values.data))

    def test_empty_fields(self):
        """Test if the API can reject empty fields
        """
        empty_fields = {'email': '', 'username': '', 'password': ''}
        return_values = self.client().post('/auth/register', data=empty_fields)
        self.assertEqual(return_values.status_code, 422)
        self.assertIn('Please fill all the fields', str(return_values.data))

    def test_password_length(self):
        """Test if the API can reject a password with less than 7 characters
        """
        password_length = {'email': 'kaguna@gmail.com', 'username': 'james', 'password': 'j123'}
        return_values = self.client().post('/auth/register', data=password_length)
        self.assertEqual(return_values.status_code, 412)
        self.assertIn('The password is too short', str(return_values.data))

    def test_user_email_existence(self):
        """Test if the API can reject a user who exists in the database
        """
        return_values = self.client().post('/auth/register', data=self.users)
        self.assertEqual(return_values.status_code, 201)
        self.assertIn('User registered successfully', str(return_values.data))

        return_values = self.client().post('/auth/register', data=self.users)
        self.assertEqual(return_values.status_code, 409)
        self.assertIn('User exists!', str(return_values.data))

    """User reset password"""

    def test_successful_user_reset_password(self):
        """Test API can reset password
        """
        self.client().post('/auth/register', data=self.users)
        new_password_details = {'email': 'kaguna@gmail.com', 'password': 'james123', 'retyped_password': 'james123'}
        response = self.client().put('/auth/reset_password', data=new_password_details)
        self.assertEqual(response.status_code, 201)
        self.assertIn('Password resetting is successful', str(response.data))

    def test_reset_password_with_invalid_email(self):
        """Test API can reset password with invalid email
        """
        self.client().post('/auth/register', data=self.users)
        new_password_details = {'email': 'kagunagmail.com', 'password': 'james123', 'retyped_password': 'james123'}
        response = self.client().put('/auth/reset_password', data=new_password_details)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid email given', str(response.data))

    def test_reset_password_with_short_password(self):
        """Test API can reset password with short password
        """
        self.client().post('/auth/register', data=self.users)
        new_password_details = {'email': 'kaguna@gmail.com', 'password': 'jam', 'retyped_password': 'jam'}
        response = self.client().put('/auth/reset_password', data=new_password_details)
        self.assertEqual(response.status_code, 412)
        self.assertIn('The password is too short', str(response.data))

    def test_reset_password_with_password_mismatch(self):
        """Test API can reset password with password mismatch
        """
        self.client().post('/auth/register', data=self.users)
        new_password_details = {'email': 'kaguna@gmail.com', 'password': 'james123', 'retyped_password': 'pass123'}
        response = self.client().put('/auth/reset_password', data=new_password_details)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Password mismatch', str(response.data))

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

    # Make the tests conveniently executable
    if __name__ == "__main__":
        unittest.main()
