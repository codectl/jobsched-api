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
    LOG_LEVEL = "INFO"


class DevelopmentSettings(_Settings):
    ENV = "development"
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class TestingSettings(_Settings):
    ENV = "testing"
    TESTING = True
    LOG_LEVEL = "DEBUG"


def swagger_configs(app_root="/"):
    prefix = "" if app_root == "/" else app_root
    return {
        "url_prefix": prefix,
        "swagger_route": "/",
        "swagger_static": "/static",
        "swagger_favicon": "favicon.ico",
        "swagger_hide_bar": True,
    }


def settings_class(environment: str):
    """Link given environment to a config class."""
    return getattr(sys.modules[__name__], f"{environment.capitalize()}Settings")
