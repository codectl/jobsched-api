import sys
from enum import Enum
from typing import Optional

from pydantic import BaseSettings, Field, root_validator


class _SchedType(Enum):
    PBS = "pbs"
    SLURM = "slurm"
    TORQUE = "torque"


class _Sched(BaseSettings):
    EXEC_PATH: Optional[str] = Field(None, env="EXEC")
    HOME_PATH: Optional[str] = Field(None, env="HOME")
    SERVER: Optional[str] = None

    class Config(BaseSettings.Config):
        @classmethod
        def prepare_field(cls, field) -> None:
            field_info_from_config = cls.get_field_info(field.name)
            env = field_info_from_config.get('env') or field.field_info.extra.get('env')
            env_names = {cls.env_prefix + (field.name if env is None else env)}
            if not cls.case_sensitive:
                env_names = env_names.__class__(n.lower() for n in env_names)
            field.field_info.extra['env_names'] = env_names


class _Settings(BaseSettings):
    ENV: str
    LOG_LEVEL: str = "INFO"

    DEBUG: bool = False
    TESTING: bool = False

    # application root context
    APPLICATION_ROOT: str = "/"

    # OPENAPI supported version
    OPENAPI: str = "3.0.3"

    SCHED_TYPE: _SchedType
    SCHED: _Sched

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @root_validator(pre=True)
    def parse_sched(cls, values):
        sched = _Sched
        sched_type = _SchedType[values["SCHED_TYPE"]]
        sched.Config.env_prefix = sched_type.name + "_"
        for field in _Sched.__fields__.values():
            sched.Config.prepare_field(field)
        values["SCHED"] = sched()
        values["SCHED_TYPE"] = sched_type
        return values


class ProductionSettings(_Settings):
    ENV = "production"


class DevelopmentSettings(_Settings):
    ENV = "development"
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class TestingSettings(_Settings):
    ENV = "testing"
    TESTING = True


def settings_class(environment: str) -> type[_Settings]:
    return getattr(sys.modules[__name__], f"{environment.capitalize()}Settings")


def swagger_configs(app_root="/") -> dict:
    prefix = "" if app_root == "/" else app_root
    return {
        "url_prefix": prefix,
        "swagger_route": "/",
        "swagger_static": "/static",
        "swagger_favicon": "favicon.ico",
        "swagger_hide_bar": True,
    }
