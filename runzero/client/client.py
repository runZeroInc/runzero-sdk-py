"""
client provides the runZero platform Client which must be provided to all objects which interact
with the runZero API.
"""
from enum import Enum
from typing import Any, Optional
from urllib.parse import urlparse

import requests
from pydantic import BaseModel
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import ConnectTimeout as RequestsConnectTimeout
from requests.exceptions import ContentDecodingError
from requests.exceptions import HTTPError as RequestsHTTPError

from ._http.auth import OAuthToken, RegisteredAPIClient
from ._http.io import Request, Response
from .errors import AuthError


class Client:
    """
    The authenticated connection to your runZero service destination.

    A client must be built and provided to objects which interact
    with the runZero API. It is responsible for authentication
    and communication, and instantiation should be your first step
    in doing just about anything in this SDK.

    :param account_key: Optional account key, sometimes known as client key, which
        is a high-privilege key which grants the holder the rights of an org_key across
        all organizations in the account, as well as additional administrative actions.
        Account keys are 30-character hexadecimal strings that with 'CT'. Set this value,
        use an org_key, or use Oauth by calling register_api_client(). OAuth should be
        preferred.

    :param org_key: Optional organization key which grants the holder rights
        to operations confined to a specific runZero organization.
        Org keys are 30-character hexadecimal strings that with 'OT'. Set this value,
        use an account_key, or use Oauth by calling register_api_client(). OAuth should be
        preferred.

    :param server_url: Optional URL to the server hosting the API. Self-hosted API
        server targets must provide the server url in string form,
        e.g. 'https://runzero.local:8443'
        If not provided, the default hosted infrastructure URL
        'https://console.runzero.com' is used.
    :type validate_certificate: bool

    :param validate_certificate: Optional bool to change whether Client checks
        the validity of the API server's certificate before proceeding. We recommend
        not setting this to false unless you are doing local development or testing.
        Ignoring certificate validation errors can result in credential theft or other
        bad outcomes.
    :type validate_certificate: bool
    """

    __default_timeout__ = 30
    __default_server_url__ = "https://console.runzero.com"

    class _Paths(str, Enum):
        """Enum of resource paths for the runZero APIs"""

        TOKEN = "api/v1.0/account/api/token"

    class _AuthScope(Enum):
        """Enum of auth scopes for the runZero APIs"""

        ACCOUNT = 1
        ORG = 2

    def __init__(
        self,
        account_key: Optional[str] = None,
        org_key: Optional[str] = None,
        server_url: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        validate_certificate: Optional[bool] = None,
    ):
        """Constructor method"""
        self.__account_key: Optional[str] = account_key
        self.__org_key: Optional[str] = org_key
        self._use_token: bool = False
        self.__client_id: Optional[str] = None
        self.__client_secret: Optional[str] = None
        self.__token: Optional[OAuthToken] = None
        server_url = server_url or self.__default_server_url__
        parsed = urlparse(server_url)
        if not all([parsed.scheme, parsed.netloc]):
            raise ValueError(f"Url {server_url} is not valid")
        if not parsed.scheme == "https":
            raise ValueError(f"Url {server_url} must be https")
        self.server_url = server_url
        if timeout_seconds is not None and timeout_seconds <= 0:
            raise ValueError("Timeout must be greater than 0")
        self._timeout = timeout_seconds or self.__default_timeout__
        if validate_certificate is None:
            self._validate_cert = True
        else:
            self._validate_cert = validate_certificate

    @property
    def oauth_token_is_expired(self) -> bool:
        """Returns true if the oauth token is no longer valid.

        Note that the token is automatically refreshed for you when
        possible. This value doesn't need to be checked and manually
        refreshed in most cases.

        :return bool: indicating whether the oauth token is expired.
             If OAuth is not in-use with the client, value is always false.
        """
        if self.__token:
            return self.__token.is_expired()
        return False

    @property
    def oauth_active(self) -> bool:
        """
         Returns true if the OAuth is in use.
             This happens when register_api_client was called successfully

        :return bool: indicating whether the oauth token is expired.
             If there is no oauth used with the client, value is always false.
        """
        return self._use_token

    def oauth_login(self, client_id: str, client_secret: str) -> None:
        """
        Registers the runZero SDK client using OAuth credentials, and
        enables the Client to use OAuth.

        To obtain a client ID and client secret, see the API Clients area
        of the product. Generation of these values is restricted to account
        administrators.

        :param client_id: The client ID for the runZero registered API client
        :param client_secret: The client secret for the runZero registered API client
        :raise AuthError: Exception for invalid OAuth configurations
        """
        self.__client_id = client_id
        self.__client_secret = client_secret
        self._use_token = True
        return self._login()

    @property
    def url(self) -> str:
        """The url of the server

        :return: str: The URL of the runZero server
        """
        return self.server_url

    # This is only used if the auth type is a registered api client
    def _login(self) -> None:
        """
        Attempts to use the client secret and client id to generate an OAuth token.

        :raise AuthError
        """
        if not self._use_token or (self.__client_id is None or self.__client_secret is None):
            raise AuthError("invalid auth configuration")
        try:
            resp = requests.post(
                f"{self.server_url}/{self._Paths.TOKEN.value}",
                data=RegisteredAPIClient(self.__client_id, self.__client_secret).register(),
                timeout=self._timeout,
                verify=self._validate_cert,
            )
            resp.raise_for_status()
            self.__token = resp.json(object_hook=OAuthToken.parse_obj)
        except (
            RequestsConnectTimeout,
            RequestsConnectionError,
            RequestsHTTPError,
            ContentDecodingError,
            ConnectionRefusedError,
        ) as exc:
            raise AuthError("failed to authenticate") from exc

    def _get_auth_token(self, scope: _AuthScope) -> str:
        """
        Validates and resolves the bearer token to use depending on the provided API scope.

        Will also refresh the OAuth token if it's about to expire.

        :param scope: Authentication scope for the requested credential to resolve
        :return: Bearer token for the required API scope
        :rtype string
        :raise AuthError
        """
        self._validate_scope_permissions(scope)

        if self._use_token:
            if self.__token is not None:
                # this handles refreshing the token if necessary
                if self.__token.is_expired():
                    self._login()
                return self.__token.access_token
        if scope == self._AuthScope.ACCOUNT:
            if self.__account_key is not None:
                return self.__account_key
        if scope == self._AuthScope.ORG:
            if self.__account_key is not None:
                return self.__account_key
            if self.__org_key is not None:
                return self.__org_key
        raise AuthError("invalid credential configurations")

    def _validate_scope_permissions(self, scope: _AuthScope) -> None:
        if self._use_token:
            if self.__token is None:
                raise AuthError("no valid OAuth token")
            return
        if scope is self._AuthScope.ACCOUNT:
            if self.__account_key is None:
                raise AuthError("missing account key")
            return
        if scope is self._AuthScope.ORG:
            if self.__org_key is None:
                if self.__account_key is None:
                    raise AuthError("missing organization or account key")
            return

    @property
    def timeout(self) -> int:
        """
        The set request timeout value in seconds
        :return: int
        """
        return self._timeout

    @property
    def validate_cert(self) -> bool:
        """
        Boolean indicating whether the https cert must valid before proceeding.
        :return: bool
        """
        return self._validate_cert

    def execute(
        self,
        method: str,
        endpoint: str,
        params: Optional[Any] = None,
        data: Optional[BaseModel] = None,
        files: Optional[Any] = None,
        multipart: Optional[bool] = None,
    ) -> Response:
        """Executes the request

        :param method: The REST verb to use
        :param endpoint: The path to execute against
        :param params: URL query parameters
        :param data: The data to send in form body (POST, PATCH, PUT)
        :param files: For multipart form data or file uploads. Format varies.
        :param multipart: True if using a multipart form data (combination file[s] and form data)
        :return: The result of the execution as class:.`Response`
        :raises ValidationError, ConnTimeoutError, ConnError, CommunicationError
        """
        token: str = ""
        try:
            token = self._get_auth_token(self._AuthScope.ACCOUNT)
        except AuthError:
            pass

        if not token:
            token = self._get_auth_token(self._AuthScope.ORG)
        form_data = None
        if data:
            form_data = data.json()
        resp = Request(
            url=f"{self.url}/{endpoint}",
            token=token,
            method=method,
            handlers=None,
            params=params,
            timeout=self.timeout,
            validate_certificate=self.validate_cert,
            data=form_data,
            files=files,
            multipart=multipart,
        ).execute()
        # If the result doesn't have JSON decoded, it's not a valid result.
        # TODO: Decide if absolutely anything else else should be a raised error here
        return resp
