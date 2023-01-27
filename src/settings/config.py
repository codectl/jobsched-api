import sys

from pydantic import BaseSettings


class _Settings(BaseSettings):
    ENV: str
    LOG_LEVEL: str = "INFO"

    DEBUG: bool = False
    TESTING: bool = False

    # application root context
    APPLICATION_ROOT: str = "/"

    # OPENAPI supported version
    OPENAPI: str = "3.0.3"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


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
