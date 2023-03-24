"""
io contains classes which wrap network communication and handle errors in a consistent fashion.
"""
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
    ServerError,
    UnknownAPIError,
    UnsupportedRequestError,
)

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
        try:
            self.json_obj = response.json()
        except JSONDecodeError:
            self.json_obj = None


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
    ):
        """Class constructor"""
        self.url = url
        self.method = method
        if handlers is None:
            self.handlers = []
        else:
            self.handlers = handlers
        self.token = token
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

        self.handlers.append(_error_handler)
        req = RequestsRequest(
            method=self.method,
            url=self.url,
            headers=headers,
            params=self.params,
            data=self.data,
            files=self.files,
        )
        for handler in self.handlers:
            req.register_hook("response", handler)
        return BearerToken(self.token)(req.prepare())

    def execute(self) -> Response:
        """Sends prepared request.

        Returns
            (Response)
                The HTTP Response from an API Request
                to the server.
        """
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


def _generate_prepared_request(
    method: str,
    url: str,
    headers: Dict[str, Any],
    auth: BearerToken,
    data: Any,
    params: Dict[str, Any],
    handlers: List[HandlerType],
) -> PreparedRequest:
    request = RequestsRequest(
        method=method,
        url=url,
        headers=headers,
        auth=auth,
        data=data,
        params=params,
    )

    handlers.append(_error_handler)

    for handler in handlers:
        request.register_hook("response", handler)

    return request.prepare()


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
            # {"detail":"sourceId UUID cannot be all zeroes","error":"request failed","status":"error",
            # "title":"request failed"}
            try:
                error_info = ErrInfo(
                    detail=body.pop("detail"),
                    status=response.status_code,
                    title=body.pop("title"),
                )
            except KeyError:
                pass
    except (KeyError, JSONDecodeError) as exc:
        raise UnknownAPIError(str(response), response.reason) from exc

    if 400 <= response.status_code <= 499:
        raise ClientError(
            unparsed_response=str(response),
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
