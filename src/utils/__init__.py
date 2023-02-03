from copy import deepcopy
from dataclasses import asdict
from typing import Dict, Type

from apispec_plugins.types import HTTPResponse
from flask_restful import abort
from pydantic import BaseModel
from pydantic.utils import lenient_issubclass
from werkzeug.http import HTTP_STATUS_CODES


def build_extra(model: Type[BaseModel], values: dict[str, Dict]):
    for field in model.__fields__.values():
        if lenient_issubclass(field.type_, BaseModel):
            build_extra(field.type_, values)

        if field.alias in values:
            values.pop(field.alias)

    return values


def unflatten(model: Type[BaseModel], values: dict[str, Dict]):
    parsed, objs = deepcopy(values), []

    for field in model.__fields__.values():
        if lenient_issubclass(field.type_, BaseModel):
            objs.append(field)
        else:
            if field.alias in values:
                values.pop(field.alias)

    for field in objs:
        if field.alias in values:
            values.update(values[field.alias])
            values.pop(field.alias)

        parsed[field.alias] = unflatten(field.type_, values)

    return parsed


def http_response(code: int, description=""):
    reason = HTTP_STATUS_CODES[code]
    description = f"{reason}: {description}" if description else reason
    return asdict(HTTPResponse(code=code, description=description))


def abort_with(code: int, description=""):
    abort(code, **http_response(code, description=description))
