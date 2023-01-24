from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_plugins.types import AuthSchemes, Server, Tag
from apispec_plugins.utils import base_template
from apispec_plugins.webframeworks.flask import FlaskPlugin
from apispec_ui.flask import Swagger
from flask import Blueprint, Flask
from flask_cors import CORS

from src import __description__, __title__, __version__
from src.settings.ctx import ctx_settings
from src.settings.config import settings_class, swagger_configs


def create_app(environ="development", configs=None):
    """Create a new app."""

    # define the WSGI application object
    app = Flask(__name__, static_folder=None)

    config = settings_class(environ)().dict()
    config.update(configs or {})
    app.config.update(config)

    setup_app(app)

    return app


def setup_app(app):
    """Initial setups."""
    CORS(app)  # enable CORS

    url_prefix = app.config["APPLICATION_ROOT"]
    openapi_version = app.config["OPENAPI"]

    # initial blueprint wiring
    index = Blueprint("index", __name__)
    app.register_blueprint(index, url_prefix=url_prefix)

    spec_template = base_template(
        openapi_version=openapi_version,
        info={
            "title": __title__,
            "version": __version__,
            "description": __description__,
        },
        servers=[Server(url=url_prefix, description=app.config["ENV"])],
        auths=[AuthSchemes.BasicAuth()],
        tags=[
            Tag(
                name="filesystem",
                description="CRUD operations over files in the current filesystem",
            ),
            Tag(
                name="file manager",
                description="Actions that serve React component named File Manager",
            ),
        ],
    )

    spec = APISpec(
        title=__title__,
        version=__version__,
        openapi_version=openapi_version,
        plugins=(FlaskPlugin(), MarshmallowPlugin()),
        **spec_template
    )

    # create paths from app views
    for view in app.view_functions.values():
        spec.path(view=view, app=app, base_path=url_prefix)

    # create views for Swagger
    Swagger(app=app, apispec=spec, config=swagger_configs(app_root=url_prefix))

    # settings within app ctx
    ctx_settings(app)
