"""
Management of asset custom data sources.
"""
import uuid
from typing import List, Optional

from runzero.client import Client
from runzero.types import Organization, OrgOptions


class OrgsAdmin:
    """Management of runZero organizations.

    Organizations are an administrative boundary for various platform-level objects and methods.

    :param client: A handle to the :class:`runzero.Client` client which manages interactions
        with the runZero server.
    """

    _ENDPOINT = "api/v1.0/account/orgs"

    def __init__(self, client: Client):
        """Constructor method"""
        self._client = client

    def get_all(self) -> List[Organization]:
        """
        Retrieves all runZero Organizations available to your account

        :return: A list of all Organizations available to your account
        :raises AuthError, ClientError, ServerError
        """
        res = self._client.execute("GET", self._ENDPOINT)
        result: List[Organization] = []
        for org in res.json_obj:
            result.append(Organization.parse_obj(org))
        return result

    def get(self, org_id: Optional[uuid.UUID] = None, name: Optional[str] = None) -> Optional[Organization]:
        """
        Retrieves the runZero Organization with the provided name or id, if it exists in your account.

        :param org_id: Optional id of the organization you want returned
        :param name: Optional name of the organization you want returned
        :return: Organization if found, or None
        :raises AuthError, ClientError, ServerError
        """
        if name is None and org_id is None:
            raise ValueError("must provide org_id or organization name")
        if org_id is not None:
            res = self._client.execute("GET", f"{self._ENDPOINT}/{str(org_id)}")
            return Organization.parse_obj(res.json_obj)
        # name
        for org in self.get_all():
            if org.name == name:
                return org
        return None

    def create(self, org_options: OrgOptions) -> Optional[Organization]:
        """
        Creates a new organization in your account.

        :param org_options: Description of organizaiton to create
        :return Organization created or None
        :raises AuthError, ClientError, ServerError
        """
        res = self._client.execute("PUT", self._ENDPOINT, data=org_options)
        obj = res.json_obj
        data_obj = obj.get("data", "")
        if data_obj:
            obj = data_obj

        return Organization.parse_obj(obj)

    def update(self, org_id: uuid.UUID, org_options: OrgOptions) -> Optional[Organization]:
        """
        Updates an organization associated with your account.

        :param org_id: The ID of the Organization to patch
        :param org_options: Organization's updated values
        :return Organization updated or None
        :raises AuthError, ClientError, ServerError
        """
        res = self._client.execute("PATCH", f"{self._ENDPOINT}/{str(org_id)}", data=org_options)
        return Organization.parse_obj(res.json_obj)

    def delete(self, org_id: uuid.UUID) -> None:
        """
        Deletes an organization with provided ID from your account.

        :param org_id: The ID of the organization to operate against
        :return Organization deleted or None
        :raises AuthError, ClientError, ServerError
        """
        self._client.execute("DELETE", f"{self._ENDPOINT}/{org_id}")
