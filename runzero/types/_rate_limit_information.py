"""A single class which holds the rate limit information returned from the server"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class RateLimitInformation:
    """Describes rate limits to API users.

    See https://www.runzero.com/docs/leveraging-the-api/#api-client-credentials for details.

    :param usage_limit: int, optional which holds the number of API requests possible. The value is related to
        the license associated with the caller.
    :type usage_limit: int or None

    :param usage_remaining: int, optional which holds the number of API requests left before the request
        is rejected by the server with a rate limit error message.
    :type usage_remaining: int or None

    :param usage_today: int, optional which holds the number of API requests made in the current day period.
    :type usage_today: int or None

    :param usage_total: int, optional which holds the number of API requests made with the given credential.
    :type usage_total: int or None

    """

    usage_limit: Optional[int]
    usage_remaining: Optional[int]
    usage_today: Optional[int]
    usage_total: Optional[int]

    @classmethod
    def from_headers(cls, headers: Any) -> RateLimitInformation:
        """Class constructor method"""

        try:
            return cls(
                usage_limit=int(headers["X-API-Usage-Limit"]),
                usage_remaining=int(headers["X-API-Usage-Remaining"]),
                usage_today=int(headers["X-API-Usage-Today"]),
                usage_total=int(headers["X-API-Usage-Total"]),
            )
        except (AttributeError, ValueError, KeyError):
            # unlikely, but requests defines headers as 'any' though it is
            # typically their own case-insensitive dict type.
            # and the runZero server should always return numeric data
            pass

        return cls(
            usage_limit=None,
            usage_remaining=None,
            usage_today=None,
            usage_total=None,
        )

    def __str__(self) -> str:
        """A friendly string"""
        return (
            f"Limit: {self.usage_limit}, Remaining: {self.usage_remaining}, Usage Today: {self.usage_today}, Total "
            f"Usage: {self.usage_total}"
        )
