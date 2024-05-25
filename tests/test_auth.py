import pytest
from flask import g, session
from flaskr.db import get_db

# Test case for user registration
def test_register(client, app):
    # Ensure the registration page is accessible
    assert client.get('/auth/register').status_code == 200
    # Test user registration
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    # Ensure the user is redirected to the login page after registration
    assert response.headers["Location"] == "/auth/login"

    # Check that the new user is added to the database
    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None

# Test case for validating user registration input
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'), # Test for empty username
    ('a', '', b'Password is required.'), # Test for empty password
    ('test', 'test', b'already registered'), # Test for existing user
))
def test_register_validate_input(client, username, password, message):
    # Test user registration with different inputs
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    # Ensure the appropriate error message is returned
    assert message in response.data

# Test case for user login
def test_login(client, auth):
    # Ensure the login page is accessible
    assert client.get('/auth/login').status_code == 200
    # Test user login
    response = auth.login()
    # Ensure the user is redirected to the homepage after login
    assert response.headers["Location"] == "/"

    # Check that the user's session is stored
    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'

# Test case for validating user login input
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'), # Test for non-existing user
    ('test', 'a', b'Incorrect password.'), # Test for wrong password
))
def test_login_validate_input(auth, username, password, message):
    # Test user login with different inputs
    response = auth.login(username, password)
    # Ensure the appropriate error message is returned
    assert message in response.data

# Test case for user logout
def test_logout(client, auth):
    # Test user login
    auth.login()

    # Test user logout
    with client:
        auth.logout()
        # Ensure the user's session is cleared after logout
        assert 'user_id' not in session