from werkzeug.exceptions import HTTPException

from flask import redirect, url_for

from src.utils import http_response


def ctx_settings(app):

    # redirect root path to context root
    app.add_url_rule("/", "index", view_func=lambda: redirect(url_for("swagger.ui")))

    @app.errorhandler(HTTPException)
    def handle_http_errors(ex):
        return http_response(code=ex.code), ex.code
