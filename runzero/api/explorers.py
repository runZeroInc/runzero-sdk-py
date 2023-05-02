"""
Management of an Organization's explorers, which perform scan activity.
"""

import uuid
from typing import List, Optional

from runzero.client import Client
from runzero.types import Explorer, ExplorerSiteID

__all__ = [
    "Explorers",
]


class Explorers:
    """Management of runZero Explorers.

    Explorers are deployed to a machine and are assigned to :class:`runzero.api.Sites` where
    they perform Scans defined by :class:`runzero.api.Tasks`.

    Explorers are simliar to :class:`runzero.api.HostedZones` in that both execute tasks.
    Whereas HostedZones are provided by runZero and do the work of Explorers, an Explorer is a single
    deployable service which can scan networks which are not publicly accessible.

    :param client: A handle to the :class:`runzero.Client` client which manages interactions
        with the runZero server.
    """

    _ENDPOINT = "api/v1.0/org/explorers"

    def __init__(self, client: Client):
        """Constructor method"""
        self._client = client

    def get_all(self, org_id: uuid.UUID) -> List[Explorer]:
        """
        Retrieves all active runZero Explorers available within the given Organization.

        :param org_id: The ID of the organization to operate against

        :returns: a list of all Explorers available within the given Organization
        :raises: AuthError, ClientError, ServerError

        """
        params = {"_oid": org_id}
        res = self._client.execute("GET", self._ENDPOINT, params=params)
        result: List[Explorer] = []
        for explorer in res.json_obj:
            result.append(Explorer.parse_obj(explorer))
        return result

    def get(
        self, org_id: uuid.UUID, name: Optional[str] = None, explorer_id: Optional[uuid.UUID] = None
    ) -> Optional[Explorer]:
        """
        Retrieves the runZero Explorer with the provided name or id, if it is active and exists in the Organization.

        :param org_id: The ID of the organization to operate against
        :param name: Optional name of the explorer to retrieve. This is a case-insensitive hostname match.
            If not provided, must provide explorer_id.
        :param explorer_id: Optional id of the explorer to retrieve. If not provided, must provide name.

        :returns: explorer requested or None
        :raises: AuthError, ClientError, ServerError,
            ValueError if neither explorer_id nor name are provided.
        """
        params = {"_oid": org_id}
        if name is None and explorer_id is None:
            raise ValueError("must provide explorer_id or explorer name")
        if explorer_id is not None:
            res = self._client.execute("GET", f"{self._ENDPOINT}/{explorer_id}", params=params)
            if not res:
                return None
            return Explorer.parse_obj(res.json_obj)
        for explorer in self.get_all(org_id):
            if explorer.name == name:
                return explorer
        return None

    def update_to_latest_version(self, org_id: uuid.UUID, explorer_id: uuid.UUID) -> None:
        """
        Updates an explorer with given explorer id to the latest explorer software version available.

        This will force the explorer to upgrade and restart.

        :param org_id: The ID of the organization to operate against
        :param explorer_id: The ID of the explorer to update

        :returns: None
        :raises: AuthError, ClientError, ServerError
        """
        params = {"_oid": org_id}
        self._client.execute("POST", f"{self._ENDPOINT}/{explorer_id}/update", params=params)

    def delete(self, org_id: uuid.UUID, explorer_id: uuid.UUID) -> None:
        """
        Removes and uninstalls an explorer from your Organization.

        :param org_id: The ID of the organization to operate against
        :param explorer_id: ID of explorer to delete

        :returns: None
        :raises: AuthError, ClientError, ServerError
        """
        params = {"_oid": org_id}
        self._client.execute("DELETE", f"{self._ENDPOINT}/{explorer_id}", params=params)

    def move_to_site(self, org_id: uuid.UUID, explorer_id: uuid.UUID, site_id: uuid.UUID) -> Explorer:
        """
        Moves an explorer to a different site.

        Explorers moved to a new site will no longer execute tasks defined in the old site,
        and will be available to execute tasks defined in the new site.

        :param org_id: The ID of the organization to operate against
        :param explorer_id: ID of explorer to assign to a new site
        :param site_id: ID of the site the explorer will be assigned to

        :returns: The Explorer with the provided ID, assigned to new site site_id
        :raises: AuthError, ClientError, ServerError
        """
        params = {"_oid": org_id}
        res = self._client.execute(
            "PATCH",
            f"{self._ENDPOINT}/{explorer_id}",
            params=params,
            data=ExplorerSiteID(site_id=site_id),
        )
        return Explorer.parse_obj(res.json_obj)
