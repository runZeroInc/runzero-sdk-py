"""
Management of an Organization's hosted zones, which perform scan activity.
"""

import uuid
from typing import List, Optional

from runzero.client import Client
from runzero.types import HostedZone

__all__ = [
    "HostedZones",
]


class HostedZones:
    """Management of runZero hosted zones.

    A hosted zone is a pool of cloud-hosted :class:`runzero.api.Explorers`
    available to Enterprise customers.

    Instead of specifing a single manually deployed explorer, a hosted zone may be specified
    when working with :class:`runzero.api.Tasks` or :class:`runzero.api.Templates`. Hosted zones
    can only reach public IP space.

    :param client: A handle to the :class:`runzero.Client` client which manages interactions
        with the runZero server.
    """

    _ENDPOINT = "api/v1.0/org/hosted-zones"

    def __init__(self, client: Client):
        """Constructor method"""
        self._client = client

    def get_all(self, org_id: uuid.UUID) -> List[HostedZone]:
        """
        Retrieves all active runZero hosted zones available within the given organization.

        :param org_id: The ID of the organization to operate against

        :returns: list of HostedZones
        :raises: AuthError, ClientError, ServerError

        """
        params = {"_oid": org_id}
        res = self._client.execute("GET", self._ENDPOINT, params=params)
        result: List[HostedZone] = []
        for hosted_zone in res.json_obj:
            result.append(HostedZone.parse_obj(hosted_zone))
        return result

    def get(
        self, org_id: uuid.UUID, name: Optional[str] = None, hosted_zone_id: Optional[uuid.UUID] = None
    ) -> Optional[HostedZone]:
        """
        Retrieves the runZero hosted zone with the provided name or id, if it is active and exists in the Organization.

        :param org_id: The ID of the organization to operate against
        :param name: Optional name of the hosted zone to retrieve. This is a case-insensitive match.
            If not provided, must provide hosted_zone_id.
        :param hosted_zone_id: Optional id of the hosted zone to retrieve. If not provided, must provide name.

        :returns: HostedZone requested or None
        :raises: AuthError, ClientError, ServerError,
            ValueError if neither hosted_zone_id nor name are provided.
        """
        params = {"_oid": org_id}
        if name is None and hosted_zone_id is None:
            raise ValueError("must provide hosted_zone_id or hosted zone name")
        if hosted_zone_id is not None:
            res = self._client.execute("GET", f"{self._ENDPOINT}/{hosted_zone_id}", params=params)
            if not res:
                return None
            return HostedZone.parse_obj(res.json_obj)
        # name
        for hosted_zone in self.get_all(org_id):
            if hosted_zone.name == name:
                return hosted_zone
        return None
