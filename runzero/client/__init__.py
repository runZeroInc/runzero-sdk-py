"""client provides the Client object and related utilities.

The Client is responsible for communication with runZero services.
"""

from runzero.client.client import Client
from runzero.client.errors import AuthError, ClientError, ServerError

__all__ = [
    "AuthError",
    "Client",
    "ClientError",
    "ServerError",
]
