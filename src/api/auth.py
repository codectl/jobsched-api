from functools import wraps

from flask import g, request
from werkzeug.local import LocalProxy

from src.services.auth import AuthSvc
from src.utils import abort_with


# proxy to load username
current_username = LocalProxy(lambda: load_user())


def load_user():
    """Load user from request context."""
    return getattr(g, "username", None)


def requires_auth(schemes=("basic",)):
    """Validate endpoint against given authorization schemes.
    Fail if authorization properties are missing or are invalid."""

    def wrapper(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            if "basic" in schemes:
                auth = request.authorization
                if auth and AuthSvc.authenticate(
                    username=auth.username, password=auth.password
                ):
                    g.username = auth.username
                    return func(*args, **kwargs)
            elif "bearer" in schemes:
                raise NotImplementedError

            abort_with(401)

        return decorated

    return wrapper
