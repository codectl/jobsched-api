from importlib import metadata


__title__: str = metadata.metadata(__package__)["name"]
__description__: str = metadata.metadata(__package__)["summary"]
__version__: str = metadata.metadata(__package__)["version"]
__author__: str = metadata.metadata(__package__)["author"]
__license__: str = metadata.metadata(__package__)["license"]
