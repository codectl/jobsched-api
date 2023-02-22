import json

from flask import Blueprint, current_app, request
from flask_restful import Api, Resource
from pydantic import ValidationError
from werkzeug.local import LocalProxy

from src.utils import abort_with
from src.api.auth import requires_auth
from src.models.job import JobStat, JobSubmit
from src.services.pbs import PBS

blueprint = Blueprint("pbs", __name__, url_prefix="/pbs")
api = Api(blueprint)

# proxy to load PBS service
_PBS = LocalProxy(lambda: PBS(env=current_app.config["SCHED_ENV"]))


@api.resource("/qstat/<job_id>", endpoint="qstat")
class Qstat(Resource):
    @requires_auth(schemes=["basic"])
    def get(self, job_id):
        """
        get job stats given a search criteria
        ---
        tags:
            - PBS
        parameters:
            - in: path
              name: job_id
              schema:
                type: string
              required: True
              description: the id of the job to query
        responses:
            200:
                content:
                    application/json:
                        schema: JobStat
            401:
            404:
            405:
        """
        job: JobStat = _PBS.qstat(job_id)
        if not job:
            abort_with(code=404, description="job not found")
        return json.loads(job.json())


@api.resource("/qsub", endpoint="qsub")
class Qsub(Resource):
    @requires_auth(schemes=["basic"])
    def post(self):
        """
        submit a job given its properties
        ---
        tags:
            - PBS
        requestBody:
            description: job properties
            required: true
            content:
                application/json:
                    schema: JobSubmit
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
