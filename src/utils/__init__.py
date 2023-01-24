from dataclasses import asdict

from apispec_plugins.types import HTTPResponse
from flask_restful import abort
from werkzeug.http import HTTP_STATUS_CODES


def http_response(code: int, description=""):
    reason = HTTP_STATUS_CODES[code]
    description = f"{reason}: {description}" if description else reason
    return asdict(HTTPResponse(code=code, description=description))


def abort_with(code: int, description=""):
    abort(code, **http_response(code, description=description))
