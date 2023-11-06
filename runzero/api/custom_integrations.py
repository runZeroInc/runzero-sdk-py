"""
enables standard access to of runZero custom integrations, limited to read operations.
"""

import base64
import uuid
from typing import Any, List, Optional

from runzero.client import Client
from runzero.types import CustomIntegration


class CustomIntegrations:
    """Read access to custom integrations.

    This is a subset of operations available in runzero.admin.custom_integrations.CustomIntegrationsAdmin
    which allows 'write' operations for custom integrations.

    :param client: A handle to the :class:`runzero.Client` which manages interactions
        with the runZero server.
    """

    _ENDPOINT = "api/v1.0/org/custom-integrations"

    def __init__(self, client: Client):
        """Constructor method"""
        self._client = client

    def get_all(self, org_id: uuid.UUID) -> List[CustomIntegration]:
        """
        Lists all custom integrations available to your account.

        :param org_id: The ID of the organization to operate against

        :returns: List of custom integrations
        :raises: AuthError, ClientError, ServerError
        """

        params = {"_oid": org_id}
        res = self._client.execute("GET", self._ENDPOINT, params=params)
        result: List[CustomIntegration] = []
        for src in res.json_obj:
            result.append(_resp_to_source(src))
        return result

    def get(
        self, org_id: uuid.UUID, name: Optional[str] = None, custom_integration_id: Optional[uuid.UUID] = None
    ) -> Optional[CustomIntegration]:
        """
        Retrieves runZero custom integrations with either the matching ID or Name.

        :param org_id: The ID of the organization to operate against
        :param name: Optional, name of the organization you want the UUID for
        :param custom_integration_id: Optional, the id of the source to retrieve

        :raises: AuthError, ClientError, ServerError
            ValueError if neither custom_integration_id nor name are provided.
        :returns: The matching CustomIntegration or None
        """
        params = {"_oid": org_id}
        if name is None and custom_integration_id is None:
            raise ValueError("must provide custom_integration_id or source name")
        if custom_integration_id is not None:
            res = self._client.execute("GET", f"{self._ENDPOINT}/{custom_integration_id}", params=params)
            return _resp_to_source(res.json_obj)
        # name
        for src in self.get_all(org_id):
            if src.name == name:
                return src
        return None


def _resp_to_source(json_obj: Any) -> CustomIntegration:
    source = CustomIntegration.parse_obj(json_obj)
    if source.icon is not None:
        source.icon = base64.b64decode(source.icon)
    return source
