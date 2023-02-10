from flask import Blueprint, current_app, request
from flask_restful import Api, Resource
from werkzeug.local import LocalProxy

from src.utils import abort_with
from src.api.auth import requires_auth
from src.models.job import JobSubmit
from src.services.pbs import PBS

blueprint = Blueprint("pbs", __name__, url_prefix="/pbs")
api = Api(blueprint)

# proxy to load PBS service
_PBS = LocalProxy(
    lambda: PBS()
)


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
                    text/plain; charset=utf-8:
                        schema:
                            type: string
                            description: the job id
            400:
            401:
        """
        props: JobSubmit = JobSubmit.parse_obj(request.json)
        try:
            return _PBS.qsub(props)
        except Exception as ex:
            abort_with(code=400, description=str(ex))
