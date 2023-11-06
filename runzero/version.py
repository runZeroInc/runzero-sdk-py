"""holds the semver-compatible version tag"""

from importlib import metadata

try:
    __version__ = metadata.version("runzero-sdk")  # from pyproject.toml, ultimately
except metadata.PackageNotFoundError:
    __version__ = "unknown"
