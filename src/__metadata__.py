from importlib import metadata


pkg_name = "jobsched-api"
__title__: str = metadata.metadata(pkg_name)["name"]
__description__: str = metadata.metadata(pkg_name)["summary"]
__version__: str = metadata.metadata(pkg_name)["version"]
__author__: str = metadata.metadata(pkg_name)["author"]
__license__: str = metadata.metadata(pkg_name)["license"]
