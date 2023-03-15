from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_plugins.base.types import AuthSchemes, Server, Tag
from apispec_plugins.utils import base_template
from apispec_plugins.webframeworks.flask import FlaskPlugin
from apispec_ui.flask import Swagger
from flask import Blueprint, Flask
from flask_cors import CORS

from src import __description__, __title__, __version__
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
    index = Blueprint("index", __name__)
    _register_routes(parent=index)
    app.register_blueprint(index, url_prefix=url_prefix)

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


def _register_routes(parent: Blueprint):
    from src.api.pbs import QstatAPI, QsubAPI

    pbs_api = Blueprint("pbs", __name__, url_prefix="/pbs")
    pbs_api.add_url_rule("/qstat/<job_id>", view_func=QstatAPI.as_view("qstat"))
    pbs_api.add_url_rule("/qsub", view_func=QsubAPI.as_view("qsub"))

    parent.register_blueprint(pbs_api)
