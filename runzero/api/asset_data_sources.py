"""
enables standard access to of runZero asset data sources, limited to read operations.
"""
import base64
import uuid
from typing import Any, List, Optional

from runzero.client import Client
from runzero.types import AssetCustomSource


class CustomSources:
    """Read access to custom asset data sources.

    This is a subset of operations available in runzero.admin.asset_data_sources.CustomSourcesAdmin
    which allows 'write' operations for custom data sources.

    :param client: A handle to the :class:`runzero.Client` which manages interactions
        with the runZero server.
    """

    _ENDPOINT = "api/v1.0/org/sources"

    def __init__(self, client: Client):
        """Constructor method"""
        self._client = client

    def get_all(self, org_id: uuid.UUID) -> List[AssetCustomSource]:
        """
        Lists all custom asset sources available to your account.

        :param org_id: The ID of the organization to operate against
        :return: List of custom asset sources
        :raises AuthError, ClientError, ServerError
        """

        params = {"_oid": str(org_id)}
        res = self._client.execute("GET", self._ENDPOINT, params=params)
        result: List[AssetCustomSource] = []
        for src in res.json_obj:
            result.append(_resp_to_source(src))
        return result

    def get(
        self, org_id: uuid.UUID, name: Optional[str] = None, source_id: Optional[uuid.UUID] = None
    ) -> Optional[AssetCustomSource]:
        """
        Retrieves runZero custom sources with either the matching ID or Name.

        :param org_id: The ID of the organization to operate against
        :param name: Optional, name of the organization you want the UUID for
        :param source_id: Optional, the id of the source you want returned
        :raises AuthError, ClientError, ServerError
            ValueError if neither source_id nor name are provided.
        :return: The matching AssetCustomSource or None
        """
        params = {"_oid": str(org_id)}
        if name is None and source_id is None:
            raise ValueError("must provide source_id or source name")
        if source_id is not None:
            res = self._client.execute("GET", f"{self._ENDPOINT}/{str(source_id)}", params=params)
            return _resp_to_source(res.json_obj)
        # name
        for src in self.get_all(org_id):
            if src.name == name:
                return src
        return None


def _resp_to_source(json_obj: Any) -> AssetCustomSource:
    source = AssetCustomSource.parse_obj(json_obj)
    if source.icon is not None:
        source.icon = base64.b64decode(source.icon)
    return source
