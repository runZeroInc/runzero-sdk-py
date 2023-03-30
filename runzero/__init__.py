"""
runzero provides an interface to the runZero platform APIs
"""

# The Client is the first thing you should use.
# Should be imported here first because of circular import potential below
from runzero.client import Client  # isort: skip

from runzero.client import AuthError, ClientError, ServerError
from runzero.errors import APIError, Error
from runzero.types import ValidationError
from runzero.version import VERSION

__all__ = [
    "APIError",
    "Error",
    "VERSION",
    "ValidationError",
]
