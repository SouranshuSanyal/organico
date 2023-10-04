from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You do not have access to this page.', 'error')
            return redirect(url_for('auth.login'))  # Redirect to login page if user is not an admin
        return f(*args, **kwargs)
    return decorated_function