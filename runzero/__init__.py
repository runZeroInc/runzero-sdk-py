"""
runzero provides an interface to the runZero platform APIs
"""

# The Client is the first thing you should use.
# Should be imported here first because of circular import potential below
from runzero.client import Client  # isort: skip

import runzero.version
from runzero.client import AuthError, ClientError, ServerError
from runzero.errors import APIError, Error
from runzero.types import ValidationError

__version__ = runzero.version.__version__

__all__ = [
    "__version__",
    "Client",
    "ClientError",
    "ServerError",
    "APIError",
    "Error",
    "ValidationError",
]
