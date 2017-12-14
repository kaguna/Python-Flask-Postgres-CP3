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

    def test_successful_user_registration(self):
        """Test API can create a user (POST request)"""
        res = self.client().post('/auth/user/', data=self.users)
        self.assertEqual(res.status_code, 201)
        self.assertIn('User registered successfully', str(res.data))

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

    # Make the tests conveniently executable
    if __name__ == "__main__":
        unittest.main()

