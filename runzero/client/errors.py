"""all client errors listed here"""

from __future__ import annotations

from typing import Optional

from runzero.errors import APIError, Error
from runzero.types import RateLimitInformation
from runzero.types.errors import RFC7807Error


class UnsupportedRequestError(ValueError, Error):
    """
    UnsupportedRequestError is a named Exception class representing any Error from the runZero API
    which cannot be properly interpreted into a friendlier form.
    """

    def __init__(self, message: str):
        super().__init__(message)


class ErrInfo(RFC7807Error):
    """runZero's implementation of RFC7807 JSON error description"""

    def __init__(self, detail: str, status: int, title: str):
        super().__init__(title=title, status=status, detail=detail)

    def __repr__(self) -> str:
        return f"Error: Details:{self.detail}, Status:{self.status}, Title:{self.title}"


class ClientError(APIError):
    """
    ClientError is a named Exception class for holding 400 level http status code messages.

    :param error_info: :class:`.ErrInfo`, optional which holds message data parsed from the
        server's response.
    :type error_info: ErrInfo

    :param unparsed_response: a string which holds the unparsed response body.
    :type unparsed_response: str, optional

    :param message: A top-level error description. The default value None provides a reasonable
        message.
    """

    def __init__(
        self,
        message: Optional[str] = None,
        unparsed_response: Optional[str] = None,
        error_info: Optional[ErrInfo] = None,
    ):
        """Constructor method"""
        if message:
            message = message.strip()
        if not message:
            message = "The request was rejected by the server."
        super().__init__(message)
        self.error_info: Optional[ErrInfo] = error_info
        self.unparsed_response: Optional[str] = unparsed_response

    def __str__(self) -> str:
        """Provide a friendly, printable error string. Otherwise, only 'message' is printed."""
        out = f"{super().__str__()}".strip()
        if self.error_info:
            out = f"{out}: {self.error_info}"
        return out


class ServerError(APIError):
    """
    ServerError is a named Exception class for holding 500 level http status code messages.

    A ServerError indicates nothing about the way the request was performed. The server cannot
    complete the task. You should retry or abort.

    :param error_info: :class:`.ErrInfo`, optional which holds message data parsed from the
        server's response.
    :type error_info: ErrInfo

    :param message: A top-level error description. The default value None provides a reasonable
        message.

    :param unparsed_response: optional string which holds the unparsed response body.
    :type unparsed_response: str, optional
    """

    def __init__(
        self,
        message: Optional[str] = None,
        unparsed_response: Optional[str] = None,
        error_info: Optional[ErrInfo] = None,
    ):
        """Constructor method"""
        if message:
            message = message.strip()
        if not message:
            message = "The server encounter an error or is unable to process the request."
        super().__init__(message)
        self.error_info: Optional[ErrInfo] = error_info
        self.unparsed_response: Optional[str] = unparsed_response

    def __str__(self) -> str:
        """Provide a friendly, printable error string. Otherwise, only 'message' is printed."""
        out = f"{super().__str__()}"
        if self.error_info:
            out = f"{out}: {self.error_info}"
        return out


class AuthError(APIError):
    """
    AuthError is a named Exception class for authentication issues with the runZero SDK client

    Common types of authentication issues are:
    * Incorrect credentials
    * Misconfigured credentials
    * Missing credentials
    """

    pass


class RateLimitError(APIError):
    """
    RateLimitError is a named Exception class errors resulting from API rate limiting.

    See https://www.runzero.com/docs/leveraging-the-api/#api-client-credentials for details.

    Consider an exponential backoff retry, or a more calculated approach by examining the returned
    numbers.

    :param message: A top-level error description. The default value None provides a reasonable
        message.

    :param unparsed_response: optional string which holds the unparsed response body.
    :type unparsed_response: str, optional

    :param rate_limit_information: a RateLimitInformation object which holds the rate limit data
    :type rate_limit_information: RateLimitInformation

    """

    def __init__(
        self,
        rate_limit_information: RateLimitInformation,
        message: Optional[str] = None,
        unparsed_response: Optional[str] = None,
    ):
        """Constructor method"""
        if not message:
            message = (
                "Too many API requests for licensed rate limit. See runZero documentation for details on API "
                "rate limiting."
            )
        super().__init__(message)
        self.message = message
        self.unparsed_response: Optional[str] = unparsed_response
        self.rate_limit_information: RateLimitInformation = rate_limit_information

    def __str__(self) -> str:
        return f"{self.message} Rate limit information: {self.rate_limit_information}"


class UnknownAPIError(APIError):
    """
    UnknownAPIError is a named Exception class raised when the response indicates a structured
    error message that cannot be parsed.

    Effort is made to receive and interpret errors returned from runZero services. These
    errors should be rare to non-existent.

    :param message: A top-level error description. The default value None provides a reasonable
        message.

    :param unparsed_response: optional string which holds the unparsed response body.
    :type unparsed_response: str, optional
    """

    def __init__(self, message: Optional[str] = None, unparsed_response: Optional[str] = None):
        """Constructor method"""
        if not message:
            message = "The server encounter an error or is unable to process the request."

        super().__init__(message)
        self.unparsed_response: Optional[str] = unparsed_response


class CommunicationError(Error):
    """
    CommunicationError is a named Exception class raised when an API request to runZero
    service cannot complete due to a protocol-level error.
    """

    pass


class ConnError(Error, ConnectionError):
    """
    ConnError is a named Exception class raised when an API request to runZero
    service cannot complete due to a packet-level error.
    """

    pass


class ConnTimeoutError(Error, TimeoutError):
    """
    ConnTimeoutError is a named Exception class raised when an API request to runZero
    service cannot complete due a failure to create or maintain a connection to a
    runZero resource. The timeout value of the Client can be adjusted.
    """

    pass
