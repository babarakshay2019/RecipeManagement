import unittest
from flask import Flask
from routes import register_routes
from models import User, session, Base, engine
from main import app
from unittest.mock import patch


class TestRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary database for testing
        Base.metadata.create_all(engine)

    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()
        self.session = session
        register_routes(self.app, RECIPES_PER_PAGE=10, session=self.session)

    def test_register_user_success(self):
        # Simulate a successful registration
        data = {'username': 'new_user',
                'email': 'new_user@example.com', 'password': 'password123'}
        response = self.client.post('/api/register', json=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json, {'message': 'User registered successfully'})

        # Check if the user is added to the database
        new_user = self.session.query(User).filter_by(
            username='new_user').first()
        self.assertIsNotNone(new_user)

        # Check if the password is set correctly
        self.assertTrue(new_user.check_password('password123'))

    def test_register_user_missing_fields(self):
        # Simulate registration with missing fields
        data = {}
        response = self.client.post('/api/register', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'error': 'Missing field(s)'})

    def test_register_user_existing_user(self):
        # Simulate registration with existing username
        existing_user = User(username='existing_user',
                             email='existing_user@example.com')
        existing_user.set_password('password123')
        self.session.add(existing_user)
        self.session.commit()

        # Attempt registration with the same username
        data = {'username': 'existing_user',
                'email': 'new_email@example.com', 'password': 'password123'}
        response = self.client.post('/api/register', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json, {'error': 'Username or email already exists'})

        # Simulate registration with existing email
        data = {'username': 'new_user',
                'email': 'existing_user@example.com', 'password': 'password123'}
        response = self.client.post('/api/register', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json, {'error': 'Username or email already exists'})

    def test_register_user_missing_username(self):
        # Simulate registration with missing username
        data = {'email': 'new_user@example.com', 'password': 'password123'}
        response = self.client.post('/api/register', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'error': 'Missing field(s)'})

    def test_register_user_missing_email(self):
        # Simulate registration with missing email
        data = {'username': 'new_user', 'password': 'password123'}
        response = self.client.post('/api/register', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'error': 'Missing field(s)'})

    def test_register_user_missing_password(self):
        # Simulate registration with missing password
        data = {'username': 'new_user', 'email': 'new_user@example.com'}
        response = self.client.post('/api/register', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'error': 'Missing field(s)'})

    def test_register_user_password_strength(self):
        # Simulate registration with weak password
        data = {'username': 'weak_password_user',
                'email': 'weak_password@example.com', 'password': '123456'}
        response = self.client.post('/api/register', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'error': 'Weak password'})


class TestLogin(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_successful_login(self):
        # Provide valid username and password
        data = {'username': 'new_user', 'password': 'password123'}
        response = self.app.post('/api/login', json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)
        self.assertEqual(response.json['message'], 'Login successful')

    def test_missing_username_or_password(self):
        # Missing username or password
        data = {'username': 'valid_username'}
        response = self.app.post('/api/login', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'],
                         'Missing username or password')

    def test_invalid_credentials(self):
        # Invalid username or password
        data = {'username': 'invalid_username', 'password': 'invalid_password'}
        response = self.app.post('/api/login', json=data)
        self.assertEqual(response.status_code, 401)
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'],
                         'Invalid username or password')

    def test_create_recipe_unauthenticated(self):
        # Simulate creating a recipe without authentication
        response = self.app.post('/api/recipes', json={})
        self.assertEqual(response.status_code, 401)
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'], 'User not authenticated')

    def test_create_recipe_authenticated(self):
        # Simulate creating a recipe with authentication
        # Assuming user is already authenticated
        with patch('routes.current_user') as mock_current_user:
            mock_current_user.is_authenticated = True
            response = self.app.post('/api/recipes', json={})
            self.assertEqual(response.status_code, 400)

    def test_get_recipes_unauthenticated(self):
        # Simulate getting recipes without authentication
        response = self.app.get('/api/recipes')
        if response.status_code == 404:
            self.assertIn('message', response.json)
            self.assertEqual(response.json['message'], 'No recipes found')
        else:
            self.assertEqual(response.status_code, 200)
            self.assertIn('message', response.json)
            self.assertEqual(
                response.json['message'], 'Recipes get successful')

    def test_get_recipes_authenticated(self):
        response = self.app.get('/api/recipes')

        if response.status_code == 200:
            # Assert that the response is successful and contains the expected data
            self.assertIn('recipes', response.json)
        elif response.status_code == 404:
            self.assertIn('message', response.json)
            self.assertEqual(response.json['message'], 'No recipes found')
        else:
            self.fail(
                f"Unexpected response status code: {response.status_code}. Response: {response.json}")


    @classmethod
    def tearDownClass(cls):
        # Drop the temporary database after all tests have finished
        Base.metadata.drop_all(engine)


if __name__ == '__main__':
    unittest.main()
