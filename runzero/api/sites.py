"""
Management of an Organization's sites
"""

import uuid
from typing import List, Optional

from runzero.client import Client
from runzero.types import Site, SiteOptions

__all__ = [
    "SiteOptions",
    "Sites",
]


class Sites:
    """Management of runZero sites.

    Assets, tasks, and other objects are contained within or associated with Sites.

    :param client: A handle to the :class:`runzero.Client` client which manages interactions
        with the runZero server.
    """

    _ENDPOINT = "api/v1.0/org/sites"

    def __init__(self, client: Client):
        """Constructor method"""
        self._client = client

    def get_all(self, org_id: uuid.UUID) -> List[Site]:
        """
        Retrieves all runZero Sites available within the given Organization

        :param org_id: The ID of the organization to operate against

        :return: a list of all Sites available within the given Organization
        :raises AuthError, ClientError, ServerError

        """
        params = {"_oid": str(org_id)}
        res = self._client.execute("GET", self._ENDPOINT, params=params)
        result: List[Site] = []
        for site in res.json_obj:
            result.append(Site.parse_obj(site))
        return result

    def get(self, org_id: uuid.UUID, name: Optional[str] = None, site_id: Optional[uuid.UUID] = None) -> Optional[Site]:
        """
        Retrieves the runZero Site with the provided name or id, if it exists in your account

        :param org_id: The ID of the organization to operate against

        :param name: Optional name of the site you want returned
        :param site_id: the id of the site you want returned
        :return: site requested or None
        :raises AuthError, ClientError, ServerError,
            ValueError if neither site_id nor name are provided.
        """
        params = {"_oid": str(org_id)}
        if name is None and site_id is None:
            raise ValueError("must provide site_id or site name")
        if site_id is not None:
            res = self._client.execute("GET", f"{self._ENDPOINT}/{str(site_id)}", params=params)
            if not res:
                return None
            obj = res.json_obj
            data_obj = obj.get("data", "")
            if data_obj:
                obj = data_obj

            return Site.parse_obj(obj)
        # name
        for site in self.get_all(org_id):
            if site.name == name:
                return site
        return None

    def create(self, org_id: uuid.UUID, site_options: SiteOptions) -> Optional[Site]:
        """
        Creates a new site in the given org.

        :param org_id: The ID of the organization to operate against

        :param site_options: Description of site to create
        :return Site created or None
        :raises AuthError, ClientError, ServerError
        """
        params = {"_oid": str(org_id)}
        res = self._client.execute("PUT", self._ENDPOINT, params=params, data=site_options)
        site_data = res.json_obj.get("data", "")
        if site_data:
            return self.get(org_id=org_id, name=site_options.name)
        return Site.parse_obj(res.json_obj)

    def update(self, org_id: uuid.UUID, site_id: uuid.UUID, site_options: SiteOptions) -> Optional[Site]:
        """
        Updates a site associated with your organization.

        :param org_id: The ID of the organization to operate against

        :param site_id: The ID of the site to update.
        :param site_options: Site's updated values
        :return Site updated or None
        :raises AuthError, ClientError, ServerError
        """
        params = {"_oid": str(org_id)}
        res = self._client.execute("PATCH", f"{self._ENDPOINT}/{str(site_id)}", params=params, data=site_options)
        site_data = res.json_obj.get("data", "")
        if site_data:
            return self.get(org_id=org_id, name=site_options.name)
        return Site.parse_obj(res.json_obj)

    def delete(self, org_id: uuid.UUID, site_id: uuid.UUID) -> None:
        """
        Deletes a site from your account.

        :param org_id: The ID of the organization to operate against

        :param site_id: Custom asset site id to delete
        :return None
        :raises AuthError, ClientError, ServerError
        """
        params = {"_oid": str(org_id)}
        self._client.execute("DELETE", f"{self._ENDPOINT}/{site_id}", params=params)
