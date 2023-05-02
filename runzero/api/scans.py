"""
Management of an Organization's sites.
"""

import uuid
from typing import Optional

from runzero.client import Client
from runzero.types import ScanOptions, Task

__all__ = [
    "Scans",
    "ScanOptions",
]


class Scans:
    """Management of runZero scans.

    Scans create tasks which modify asset inventory of a single site.

    :param client: A handle to the :class:`runzero.Client` client which manages interactions
        with the runZero server.
    """

    _ENDPOINT = "api/v1.0/org/sites"

    def __init__(self, client: Client):
        """Constructor method"""
        self._client = client

    def create(
        self,
        org_id: uuid.UUID,
        scan_options: ScanOptions,
        site_id: uuid.UUID,
    ) -> Optional[Task]:
        """
        Starts a scan to bring data into the site using provided options.

        :param org_id: The ID of the organization to operate against
        :param scan_options: ScanOptions describing the scan to perform on the given site.
        :param site_id: The ID of the site which will have inventory modified by results of the scan.

        :returns: Task
        :raises: AuthError, ClientError, ServerError
        """
        res = self._client.execute(
            "PUT", f"{self._ENDPOINT}/{site_id}/scan", params={"_oid": org_id}, data=scan_options
        )
        return Task.parse_obj(res.json_obj)
