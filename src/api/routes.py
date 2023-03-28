from src.api.pbs import QstatAPI, QsubAPI

from flask import Blueprint


def register_routes() -> Blueprint:
    index = Blueprint("index", __name__)

    api = Blueprint("pbs", __name__, url_prefix="/pbs")
    api.add_url_rule("/qstat/<job_id>", view_func=QstatAPI.as_view("qstat"))
    api.add_url_rule("/qsub", view_func=QsubAPI.as_view("qsub"))

    index.register_blueprint(api)

    return index
