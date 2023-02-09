import sys
from enum import Enum
from typing import Optional

from pydantic import BaseSettings, Field, root_validator, validator


class _SchedType(Enum):
    PBS = "pbs"
    SLURM = "slurm"
    TORQUE = "torque"


class _Sched(BaseSettings):
    SCHED_TYPE: _SchedType

    class Config:
        extra = "allow"

    class _PBSSched(BaseSettings):
        EXEC_PATH: Optional[str] = Field(..., env="PBS_EXEC")
        HOME_PATH: Optional[str] = Field(..., env="PBS_HOME")
        SERVER: Optional[str] = Field(..., env="PBS_SERVER")

    def sched(self):
        if self.SCHED_TYPE is _SchedType.PBS:
            return self._PBSSched()
        return None

    @validator("SCHED_TYPE", pre=True)
    def parse_sched(cls, value):
        return _SchedType[value]


class _Settings(BaseSettings):
    ENV: str
    LOG_LEVEL: str = "INFO"

    DEBUG: bool = False
    TESTING: bool = False

    # application root context
    APPLICATION_ROOT: str = "/"

    # OPENAPI supported version
    OPENAPI: str = "3.0.3"

    # scheduler props
    SCHED: _Sched

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @root_validator(pre=True)
    def parse_sched(cls, values):
        values["SCHED"] = _Sched().sched()
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
