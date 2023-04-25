"""holds the semver-compatible version tag"""
from importlib import metadata

try:
    __version__ = metadata.version("runzero-sdk")  # from pyproject.toml, ultimately
except Exception:  # pylint: disable=broad-exception-caught
    __version__ = "unknown"
