"""holds the semver-compatible version tag"""

from importlib import metadata

try:
    # package name matches pyproject [project].name
    __version__ = metadata.version("runzero")
except metadata.PackageNotFoundError:
    __version__ = "unknown"
