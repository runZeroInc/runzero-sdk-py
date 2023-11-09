"""
errors is a package-wide container for the bottom-level custom error types used in this package.

Some errors here may originate from the server. In these cases, we want to make the raw
server error details available, but hidden from plain view you can concentrate on what to do
in response instead of interpreting HTTP error codes.

Other errors arise from purely local interactions.

In either case, Error should be the base type if it's an error deliberately raised in this
package.

Sub-packages and modules may create their own error types in those packages, particularly
if they are not useful outside of that package, but should inherit a base type here.
"""


class Error(Exception):
    """Error is a named Exception class representing bottom-level runZero Error type.

    It is not to be raised directly, but callers can catch it and distinguish runZero
    errors from any others.
    """

    pass


class APIError(Error):
    """
    APIError is a named Exception class representing errors which are returned from
    runZero API endpoints.
    """

    pass
