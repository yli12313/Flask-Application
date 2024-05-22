# Import the os module for interacting with the operating system
import os

# Import the Flask class from the flask module
from flask import Flask

# Define a funtion to create and configure the Flask application
def create_app(test_config=None):
    # Create a Flask application with instance-relative configuration
    app = Flask(__name__, instance_relative_config=True)
    # Set the default configuration of the app
    app.config.from_mapping(
        # Use 'dev' as the secret key
        SECRET_KEY='dev',
        # Set the path of the database file
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    # If no test configuration is provided
    if test_config is None:
        # Load the instance configuration if it exists
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test configuration if provided
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Define a route for the URL '/hello'
    @app.route('/hello')
    def hello():
        # Return a simple greeting
        return 'Hello, World!'
    
    # Import the 'db' module and initialize it with the app
    from . import db
    db.init_app(app)

    # Import the 'auth' module and register its blueprint with the app
    from . import auth
    app.register_blueprint(auth.bp)

    # Import the 'blog' module and register its blueprint with the app
    from . import blog
    app.register_blueprint(blog.bp)
    # Set the endpoint for the root URL to 'index'
    app.add_url_rule('/', endpoint='index')

    # Return the configured app
    return app