# Import the function 'create_app' from the 'flaskr' module
from flaskr import create_app

# Define a function to test the configuration of the app
def test_config():
    # Assert that the app is not in testing mode by default
    assert not create_app().testing
    # Assert that the app is in testing mode when 'TESTING' is set to True
    assert create_app({'TESTING': True}).testing

# Define a function to test the '/hello' route of the app
def test_hello(client):
    # Send a GET request to the '/hello' route and store the response
    response = client.get('/hello')
    # Assert that the response data is 'Hello World!'
    assert response.data == b'Hello, World!'