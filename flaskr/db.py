# Import necessary modules
import sqlite3
import click
from flask import current_app, g

# Function to get a database connection
def get_db():
    # If 'db' not in g, a new database connection is established
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Set the row_factory to sqlite3.Row to enable name-based access to columns
        g.db.row_factory = sqlite3.Row

    # Return the database connection
    return g.db

# Function to initialize the database
def init_db():
    # Get a database connection
    db = get_db()

    # Open 'schema.sql', read it and execute the script on the database
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# Define a command line command 'init-db'
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""

    # Initialize the database
    init_db()
    # Print a success message
    click.echo('Initialized the database.')

# Function to close the database connection
def close_db(e=None):
    # Pop 'db' from g and close the connection if it exists
    db = g.pop('db', None)

    if db is not None:
        db.close()

# Function to initialize the application
def init_app(app):
    # Register the function to be called when the application context ends
    app.teardown_appcontext(close_db)
    # Add the 'init-db' command to the application
    app.cli.add_command(init_db_command)
