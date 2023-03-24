"""
auth provides authentication helper classes to support bearer and OAuth token usage
"""

from datetime import datetime
from typing import Dict

import requests
from pydantic import BaseModel, Field
from requests.auth import AuthBase


class OAuthToken(BaseModel):
    """Handles OAuth tokens for the runZero platform"""

    access_token: str = Field(...)

    token_type: str = Field(...)

    expires_in: int = Field(...)

    created_at: datetime = datetime.now()

    def is_expired(self) -> bool:
        """
        Determines if the oauth token is expired or will expire within a minute

        :return: Returns a bool of whether the token is expired or about to
        :rtype bool
        """
        delta = self.created_at - datetime.now()
        return not delta.total_seconds() <= (self.expires_in + 60)


class BearerToken(AuthBase):
    """Implements bearer token authentication scheme"""

    def __init__(self, token: str):
        self._token: str = token

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        """
        Attaches the bearer token to the request headers

        :param r: the calling requests object - which is a requests.PreparedRequest
        :return the calling object
        :rtype requests.PreparedRequest
        """
        r.headers["Authorization"] = f"Bearer {self._token}"
        return r


class RegisteredAPIClient(AuthBase):
    """Handles the runZero API client registration to retrieve a bearer token"""

    def __init__(self, client_id: str, client_secret: str):
        self._client_id: str = client_id
        self._client_secret: str = client_secret

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        """
        Attach appropriate headers to the request for api client registration

        :param r: the calling requests object - which is a requests.PreparedRequest
        :return the calling object
        :rtype requests.PreparedRequest
        """
        r.headers["Content-Type"] = "application/x-www-form-urlencoded"
        return r

    def register(self) -> Dict[str, str]:
        """
        Uses the provided OAuth credentials to construct the url for requesting the OAuth bearer token.

        :return dict containing the required components to be urlencoded for OAuth authentication
        :rtype dict
        """

        return {"grant_type": "client_credentials", "client_id": self._client_id, "client_secret": self._client_secret}
