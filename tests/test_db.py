import sqlite3

import pytest
from flaskr.db import get_db

# Test case for getting and closing the database connection
def test_get_close_db(app):
    # Ensure that the same database connection is returned within the same
    # application context
    with app.app_context():
        db = get_db()
        assert db is get_db()

    # Ensure that the database connection is closed after the application context
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    # Ensure that the error message indicates that the database connection is closed
    assert 'closed' in str(e.value)

# Test case for the init-db command
def test_init_db_command(runner, monkeypatch):
    # Class the record whether the init_db function is called
    class Recorder(object):
        called = False

    # Function to simulate the init_db function and record that it's called
    def fake_init_db():
        Recorder.called = True

    # Replace the real init_db function with the fake one
    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)
    # Invoke the init-db command
    result = runner.invoke(args=['init-db'])
    # Ensure that the command output indicates that the database is initialized
    assert 'Initialized' in result.output
    # Ensure that the init_db function is called
    assert Recorder.called