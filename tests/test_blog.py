import pytest
from flaskr.db import get_db

# Test case for index page
def test_index(client, auth):
    # Ensure the index page is accessible and contains "Log In" and "Register"
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    # Test user login and ensure the index page updates correctly
    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/1/update"' in response.data

# Test case for login required routes
@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client, path):
    # Ensure the user is redirected to the login page of not logged in
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"

# Test case for author required routes
def test_author_required(app, client, auth):
    # change the post author to another user
    with app.app_context():
        db = get_db()
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
        db.commit()

    auth.login()
    # current user can't modify other user's post
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403
    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get('/').data

# Test case for post existence check
@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
))
def test_exists_required(client, auth, path):
    # Ensure the user gets a 404 error for a non-existent post
    auth.login()
    assert client.post(path).status_code == 404

# Test case for creating a post
def test_create(client, auth, app):
    # Ensure the create page is accessible and the user can create a post
    auth.login()
    assert client.get('/create').status_code == 200
    client.post('/create', data={'title': 'created', 'body': ''})

    # Ensure the post is added to the database
    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 2

# Test case for updating a post
def test_update(client, auth, app):
    # Ensure the update page is accessible and the user can update a post
    auth.login()
    assert client.get('/1/update').status_code == 200
    client.post('/1/update', data={'title': 'updated', 'body': ''})

    # Ensure the post is updated in the database
    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post['title'] == 'updated'

# Test case for validating post creation and update
@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))
def test_create_update_validate(client, auth, path):
    # Ensure the user gets an error for invalid input
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data

# Test case for deleting a post
def test_delete(client, auth, app):
    # Ensure the user can delete a post
    auth.login()
    response = client.post('/1/delete')
    assert response.headers["Location"] == "/"

    # Ensure the post is deleted from the database
    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post is None