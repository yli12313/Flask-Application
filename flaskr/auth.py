import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

# Create a Blueprint named 'auth'. This will be used for all authentication routes.
bp = Blueprint('auth', __name__, url_prefix='/auth')

# This route allows new users to register.
@bp.route('/register', methods=('GET', 'POST'))
def register():
    # If the method is POST, the user has submitted the form.
    if request.method == 'POST':
        # Get the username and password from the form.
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # Validate that username and password are present.
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        # If there's no error, insert the new user data into the database.
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                # This will be triggered if the username is already taken.
                error = f"User {username} is already registered."
            else:
                # On successful registration, redirect the user to the login page.
                return redirect(url_for("auth.login"))

        # If there was validation error, show it to the user.
        flash(error)

    # Render the registration page.
    return render_template('auth/register.html')

# This route logs in the user.
@bp.route('/login', methods=('GET', 'POST'))
def login():
    # If the method is POST, the user has submitted the form.
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        # Fetch the user data from the database.
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        # Validate the username and password.
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        # If validation passed, log in the user and redirect to the index page.
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        # If there was validation error, show it to the user.
        flash(error)

    # Render the login page.
    return render_template('auth/login.html')

# This function runs before the view function, no matter what URL is requested
@bp.before_app_request
def load_logged_in_user():
    # Get user_id from session
    user_id = session.get('user_id')

    # If user_id is None, set g.user to None
    if user_id is None:
        g.user = None
    else:
        # Else, get user data from database and store in g.user
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    # Clear the session and redirect to index page
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    # Decorator to check if user is logged in before accessing a view
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # If g.user is None, redirect to login page
        if g.user is None:
            return redirect(url_for('auth.login'))

        # Else, access the view
        return view(**kwargs)

    return wrapped_view