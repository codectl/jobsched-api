from apispec import APISpec
from apispec_plugins import FlaskPlugin, PydanticPlugin
from apispec_plugins.base.types import AuthSchemes, Server, Tag
from apispec_plugins.utils import base_template
from apispec_ui.flask import Swagger
from flask import Flask
from flask_cors import CORS

from src import __description__, __title__, __version__
from src.api.routes import register_routes
from src.settings.ctx import ctx_settings
from src.settings.config import settings_class, swagger_configs


def create_app(environ="development", configs=None):
    # the WSGI application
    app = Flask(__name__, static_folder=None)

    config = settings_class(environ)().dict()
    config.update(configs or {})
    app.config.update(config)

    setup_app(app)

    return app


def setup_app(app):
    CORS(app)  # enable CORS

    url_prefix = app.config["APPLICATION_ROOT"]
    openapi_version = app.config["OPENAPI"]

    # route wiring
    app.register_blueprint(register_routes(), url_prefix=url_prefix)

    spec_template = base_template(
        openapi_version=openapi_version,
        info={
            "title": __title__,
            "version": __version__,
            "description": __description__,
        },
        servers=[Server(url=url_prefix)],
        auths=[AuthSchemes.BasicAuth()],
        tags=[
            Tag(
                name="PBS",
                description="Operations on the PBS scheduler",
            ),
        ],
    )

    spec = APISpec(
        title=__title__,
        version=__version__,
        openapi_version=openapi_version,
        plugins=(FlaskPlugin(), PydanticPlugin()),
        **spec_template
    )

    # create paths from app views
    for view in app.view_functions.values():
        spec.path(view=view, app=app, base_path=url_prefix)

    # create views for Swagger
    Swagger(app=app, apispec=spec, config=swagger_configs(app_root=url_prefix))

    # settings within app ctx
    ctx_settings(app)
