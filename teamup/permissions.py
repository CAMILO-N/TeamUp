from functools import wraps

from flask import abort
from flask_login import current_user, login_required


def role_required(role_name):
    """Protege una vista: sin sesión manda al login; con otro rol responde 403."""
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapper(*args, **kwargs):
            if current_user.role.name != role_name:
                abort(403)
            return view(*args, **kwargs)
        return wrapper
    return decorator
