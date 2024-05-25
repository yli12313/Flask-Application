import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

# Read SQL data from file
with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

# Fixture to setup and teardown a test app
@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    # Create test app with temporary database
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    # Initialize database and execute SQL script
    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    # Provide the app for a test
    yield app

    # Teardown after test
    os.close(db_fd)
    os.unlink(db_path)

# Fixture to create a test client
@pytest.fixture
def client(app):
    return app.test_client()

# Fixture to create a command line runner
@pytest.fixture
def runner(app):
    return app.test_cli_runner()

# Class to simulate user actions in the authentication system
class AuthActions(object):
    def __init__(self, client):
        self._client = client

    # Simulate login action
    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    # Simulate logout action
    def logout(self):
        return self._client.get('/auth/logout')

# Fixture to create an AuthActions object
@pytest.fixture
def auth(client):
    return AuthActions(client)