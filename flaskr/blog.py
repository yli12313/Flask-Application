# Import necessary modules
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

# Import login_required decorator and get_db function from local modules
from flaskr.auth import login_required
from flaskr.db import get_db

# Create a Blueprint named 'blog'
bp = Blueprint('blog', __name__)

# Define the route for the blog's homepage
@bp.route('/')
def index():
    # Get the database
    db = get_db()
    # Select blog posts from the database
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    # Render them in the 'blog/index.html' template
    return render_template('blog/index.html', posts=posts)

# Define the route for creating a new blog post
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    # If the method is POST
    if request.method == 'POST':
        # Get the title and body from form
        title = request.form['title']
        body = request.form['body']
        error = None

        # If the title is not provided, set an error message
        if not title:
            error = 'Title is required.'

        # If there is an error, flash the error
        if error is not None:
            flash(error)
        else:
            # Otherwise, insert the new post into the database
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            # And redirect to the blog's homepage
            return redirect(url_for('blog.index'))

    # If the method is not POST, render the 'blog/create.html' template
    return render_template('blog/create.html')

# Define a function to get a post
def get_post(id, check_author=True):
    # Select the post from the database
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    # If the post does not exist, return a 404 error
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    # If the post exists but the author is not the current user, return a 403 error
    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    # Return the post
    return post

# Define the route for updating a post
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    # Get the post
    post = get_post(id)

    # If the method is POST
    if request.method == 'POST':
        # Get the title and body from the form
        title = request.form['title']
        body = request.form['body']
        error = None

        # If the title is not provided, set an error message
        if not title:
            error = 'Title is required.'

        # If there is an error, flash the error
        if error is not None:
            flash(error)
        else:
            # Otherwise, update the post in the database
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            # And redirect to the blog's homepage
            return redirect(url_for('blog.index'))

    # If the method is not POST, render the 'blog/update.html' template with the post
    return render_template('blog/update.html', post=post)

# Define the rote for deleting a post
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    # Get the post
    get_post(id)
    # Delete the post from the database
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    # And redirect to the blog's homepage
    return redirect(url_for('blog.index'))