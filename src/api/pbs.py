from flask import Blueprint, current_app, request
from flask_restful import Api, Resource
from pydantic import ValidationError
from werkzeug.local import LocalProxy

from src.utils import abort_with
from src.api.auth import requires_auth
from src.models.job import JobSubmit
from src.services.pbs import PBS

blueprint = Blueprint("pbs", __name__, url_prefix="/pbs")
api = Api(blueprint)

# proxy to load PBS service
_PBS = LocalProxy(lambda: PBS(env=current_app.config["SCHED_ENV"]))


@api.resource("/qsub", endpoint="qsub")
class Qsub(Resource):
    @requires_auth(schemes=["basic"])
    def post(self):
        """
        operation for job submission
        ---
        tags:
            - PBS
        requestBody:
            description: job properties
            required: true
            content:
                application/json:
                    schema: Job
        responses:
            200:
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                job_id:
                                    type: string
                                    description: the id of the submitted job
            400:
            401:
            405:
        """
        try:
            props: JobSubmit = JobSubmit.parse_obj(request.json)
            return {"job_id": _PBS.qsub(props)}
        except ValidationError as ex:
            abort_with(code=400, description=str(ex))
