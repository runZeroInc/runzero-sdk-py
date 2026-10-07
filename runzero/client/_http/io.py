"""
io contains classes which wrap network communication and handle errors in a consistent fashion.
"""

import random
import time
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from requests import JSONDecodeError, PreparedRequest
from requests import Request as RequestsRequest
from requests import Response as RequestsResponse
from requests import Session
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import ConnectTimeout as RequestsConnectTimeout
from requests.exceptions import ContentDecodingError
from requests.exceptions import HTTPError as RequestsHTTPError

from runzero.client._http.auth import BearerToken
from runzero.client.errors import (
    AuthError,
    ClientError,
    CommunicationError,
    ConnError,
    ConnTimeoutError,
    ErrInfo,
    RateLimitError,
    ServerError,
    UnknownAPIError,
    UnsupportedRequestError,
)
from runzero.types import RateLimitInformation

ALLOWED_VERBS = frozenset(["GET", "POST", "PUT", "DELETE", "PATCH"])

DEFAULT_CONTENT_HEADERS = {"content-type": "application/json"}

if TYPE_CHECKING:
    from mypy_extensions import Arg, KwArg

    HandlerType = Callable[[Arg(RequestsResponse, "response"), KwArg(Any)], RequestsResponse]
else:
    HandlerType = Callable[[RequestsResponse], RequestsResponse]


class Response:
    """The response from an HTTP request."""

    def __init__(self, response: RequestsResponse):
        """Constructor method"""
        self.status_code = response.status_code
        self.headers = response.headers
        self.rate_limit_information = RateLimitInformation.from_headers(response.headers)
        try:
            self.json_obj = response.json()
        except JSONDecodeError:
            self.json_obj = None


# Sleep indirection so tests can observe backoff without waiting.
_sleep = time.sleep

# Defaults for retrying a request the server refused with 429 Too Many Requests.
DEFAULT_RATE_LIMIT_RETRIES = 3
DEFAULT_RATE_LIMIT_BACKOFF_SECONDS = 1.0
MAX_RATE_LIMIT_WAIT_SECONDS = 120.0


def rate_limit_wait_seconds(attempt: int, retry_after: Optional[int], backoff_seconds: float) -> float:
    """Returns how long to wait before retrying a rate-limited request.

    The server's Retry-After value wins when present. Otherwise the wait doubles per attempt from
    backoff_seconds with a little jitter. Either way the wait is capped at MAX_RATE_LIMIT_WAIT_SECONDS.
    """
    if retry_after is not None and retry_after >= 0:
        wait = float(retry_after)
    else:
        wait = backoff_seconds * (2**attempt)
        wait += random.uniform(0, wait / 4) if wait > 0 else 0  # nosec B311 - jitter, not security
    return min(wait, MAX_RATE_LIMIT_WAIT_SECONDS)


class Request:
    """A wrapper around API http requests to keep all callers in-bounds.

    :param url: The url to send the request to
    :param method: The REST verb to use
    :param handlers: A list of handler functions to apply to each request
    :param params: Any additional query parameters
    :param validate_certificate: False to disable server certificate validation. Default is True (validate).
    :param data: The data to send in form body (POST, PATCH, PUT)
    :param files: For multipart form data or file uploads. Format varies.
    :param multipart: True if using a multipart form data (combination file[s] and form data)
    :param rate_limit_retries: How many times to retry after a 429 Too Many Requests response before
        raising RateLimitError. Default is DEFAULT_RATE_LIMIT_RETRIES; 0 disables retries.
    :param rate_limit_backoff_seconds: Base wait between retries when the server sends no
        Retry-After header. Doubles per attempt.

    """

    def __init__(
        self,
        url: str,
        token: str,
        method: str,
        handlers: Optional[List[HandlerType]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        validate_certificate: Optional[bool] = None,
        data: Optional[Any] = None,
        files: Optional[Any] = None,
        multipart: Optional[bool] = None,
        rate_limit_retries: Optional[int] = None,
        rate_limit_backoff_seconds: Optional[float] = None,
    ):
        """Class constructor"""
        self.url = url
        self.method = method
        if handlers is None:
            self.handlers = []
        else:
            self.handlers = handlers
        self.token = token
        self.rate_limit_retries = DEFAULT_RATE_LIMIT_RETRIES if rate_limit_retries is None else rate_limit_retries
        self.rate_limit_backoff_seconds = (
            DEFAULT_RATE_LIMIT_BACKOFF_SECONDS if rate_limit_backoff_seconds is None else rate_limit_backoff_seconds
        )
        self.params = params
        self.timeout: Optional[int] = timeout
        if validate_certificate is None:
            self._validate_cert = True
        else:
            self._validate_cert = validate_certificate
        self.validate_certificate: Optional[bool] = validate_certificate
        self.data = data
        self.files = files
        if multipart is None:
            self.multipart = False
        else:
            self.multipart = True

    def _prepare(self) -> PreparedRequest:
        if self.method not in ALLOWED_VERBS:
            raise UnsupportedRequestError(f"Unsupported http verb {self.method}")

        headers = {}
        if not self.multipart:
            # With requests files= arg for multipart,
            # setting the content type explicitly to form/multipart
            # with boundaries is discouraged. 'requests' handles automatically.
            headers = DEFAULT_CONTENT_HEADERS

        req = RequestsRequest(
            method=self.method,
            url=self.url,
            headers=headers,
            params=self.params,
            data=self.data,
            files=self.files,
        )
        # The error handler runs last and is added per prepared request so a retry does not stack it.
        for handler in [*self.handlers, _error_handler]:
            req.register_hook("response", handler)
        return BearerToken(self.token)(req.prepare())

    def execute(self) -> Response:
        """Sends prepared request, retrying with backoff when the server answers 429 Too Many Requests.

        Returns
            (Response)
                The HTTP Response from an API Request
                to the server.
        """
        attempt = 0
        while True:
            try:
                return self._send_once()
            except RateLimitError as exc:
                if attempt >= self.rate_limit_retries:
                    raise
                _sleep(rate_limit_wait_seconds(attempt, exc.retry_after, self.rate_limit_backoff_seconds))
                attempt += 1

    def _send_once(self) -> Response:
        prepared_request = self._prepare()
        session = Session()
        try:
            response = session.send(prepared_request, verify=self.validate_certificate, timeout=self.timeout)
            return Response(response)
        except RequestsConnectTimeout as exc:
            raise ConnTimeoutError from exc
        except (RequestsConnectionError, ConnectionRefusedError) as exc:
            raise ConnError from exc
        except (RequestsHTTPError, ContentDecodingError) as exc:
            raise CommunicationError from exc


def _error_handler(response: RequestsResponse, **kwargs: Any) -> RequestsResponse:
    # pylint: disable=unused-argument
    if not 400 <= response.status_code <= 599:
        return response

    try:
        body = response.json()
    except ValueError:
        body = {}
    msg = body.get("message", response.reason)
    fields = body.get("fields", "")
    error_message = f"{str(response.status_code)}: {msg} {str(fields)}"

    if response.status_code in [400, 401]:
        if response.status_code == 401:
            raise AuthError("Authentication failure")
        # Auth errors are a special case of 401 if token isn't correct
        #
        # body = {'error': 'invalid organization token:
        # invalid account API key', 'possible_token_types': ['client'], 'provided_token_type': 'organization'}
        try:
            body = response.json()
            err = body.pop("error", "")
            if err:
                msg = f"Authentication failure: Error: {err}"
                token_err = body.pop("possible_token_types", "")
                if token_err:
                    msg += f"{token_err}, provided {body.pop('provided_token_type')} "
                    raise AuthError(msg)
        except JSONDecodeError:
            pass

    error_info = None
    try:
        content_type = response.headers.get("content-type", "")
        if not content_type:
            content_type = response.headers.get("Content-Type", "")
        if content_type.startswith("application/json") or content_type.startswith("application/problem+json"):
            body = response.json().copy()
            # {"detail":"customIntegrationId UUID cannot be all zeroes","error":"request failed","status":"error",
            # "title":"request failed"}
            try:
                error_info = ErrInfo(
                    title=body.pop("title"),
                    status=response.status_code,
                    detail=body.pop("detail", None),
                )
            except KeyError:
                pass

    except (KeyError, JSONDecodeError) as exc:
        raise UnknownAPIError(str(response), response.reason) from exc

    if 400 <= response.status_code <= 499:
        if response.status_code == 429:
            raise RateLimitError(
                rate_limit_information=RateLimitInformation.from_headers(response.headers),
                unparsed_response=response.text,
                retry_after=_retry_after_seconds(response),
            )
        raise ClientError(
            unparsed_response=response.json(),
            message=f"The request was rejected by the server: {error_message}",
            error_info=error_info,
        )

    if 500 <= response.status_code <= 599:
        raise ServerError(
            unparsed_response=str(response),
            message=f"The server encounter an error or is unable to process the request: {error_message}",
            error_info=error_info,
        )

    return response


def _retry_after_seconds(response: RequestsResponse) -> Optional[int]:
    """Returns the Retry-After header as whole seconds, or None when absent or not a delay."""
    value = response.headers.get("Retry-After")
    if value is None:
        return None
    try:
        return max(0, int(float(value)))
    except (TypeError, ValueError):
        return None
