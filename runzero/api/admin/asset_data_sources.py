"""
enables administrative management of runZero asset data sources, including write operations.

These operations are privileged and require an account token directly or an OAuth key that can generate one.
"""
import base64
import pathlib
import uuid
from pathlib import Path
from typing import Any, List, Optional, Union

from runzero.client import Client
from runzero.errors import Error
from runzero.types import AssetCustomSource, BaseAssetCustomSource, NewAssetCustomSource

from ._sdk_source_icon import _PY_ICON_BYTES


class CustomSourcesAdmin:
    """Full Management of Custom Asset data sources.

    Full management of custom data sources are descriptive registered associations
    between sources of data and assets imported which are associated with those sources.

    This is a superset of operations available in runzero.asset_data_sources.CustomSources
    which allows only read operations.

    :param client: A handle to the :class:`runzero.Client` which manages interactions
        with the runZero server.
    """

    _ENDPOINT = "api/v1.0/account/sources"

    PYTHON_ICON = _PY_ICON_BYTES
    """A default icon representing a custom source defined via this Python SDK."""

    def __init__(self, client: Client):
        """Constructor method"""
        self._client = client

    def get_all(self) -> List[AssetCustomSource]:
        """
        Lists all custom asset sources available to your account.

        :return: List of custom asset sources
        :raises AuthError, ClientError, ServerError
        """
        res = self._client.execute("GET", self._ENDPOINT)
        result: List[AssetCustomSource] = []
        for src in res.json_obj:
            result.append(_resp_to_source(src))
        return result

    def get(self, name: Optional[str] = None, source_id: Optional[uuid.UUID] = None) -> Optional[AssetCustomSource]:
        """
        Retrieves runZero custom sources with either the matching ID or Name.

        :param name: Optional, name of the organization you want the UUID for
        :param source_id: Optional, the id of the source you want returned
        :raises AuthError, ClientError, ServerError
            ValueError if neither source_id nor name are provided.
        :return: The matching AssetCustomSource or None
        """
        if name is None and source_id is None:
            raise ValueError("must provide source_id or source name")
        if source_id is not None:
            res = self._client.execute("GET", f"{self._ENDPOINT}/{str(source_id)}")
            return _resp_to_source(res.json_obj)
        # name
        for src in self.get_all():
            if src.name == name:
                return src
        return None

    def create(
        self,
        name: str,
        description: Optional[str] = None,
        icon: Optional[Union[bytes, bytearray, memoryview, Path, str]] = PYTHON_ICON,
    ) -> AssetCustomSource:
        """
        Creates a new custom asset source.

        :param name: Name of custom source to be created in to your account. The
            name may not contain spaces, tabs, or other whitespace
        :param description: Optional description of custom source to be created
        :param icon: Optional file path to, or bytes of icon data. The icon must be
            a png formatted image with a maximum size of 32x32. Icon format
            is validated by the server. The default value assigns your custom
            data source the Python logo to indicate it was created by this SDK.
            Use None to have the server choose the default Custom Source logo,
            a grey runZero logo

        :return AssetCustomSource created
        :raises AuthError, ClientError, ServerError
        """

        if isinstance(icon, (Path, str)):
            try:
                icon = pathlib.Path(icon).resolve()
                with icon.open("rb") as iconf:
                    icon = iconf.read()
            except (IOError, OSError) as exc:
                raise Error from exc
        if isinstance(icon, (bytes, bytearray, memoryview)):
            icon = base64.b64encode(icon).decode("utf-8")
        req = NewAssetCustomSource(name=name, description=description, icon=icon)
        res = self._client.execute("POST", self._ENDPOINT, data=req)
        return _resp_to_source(res.json_obj)

    def update(self, source_id: uuid.UUID, source_options: BaseAssetCustomSource) -> AssetCustomSource:
        """
        Updates a custom asset source associated with your account.

        :param source_id: Custom asset source with updated values
        :param source_options: Custom asset source request values to update
        :return AssetCustomSource updated
        :raises AuthError, ClientError, ServerError
        """
        res = self._client.execute("PATCH", f"{self._ENDPOINT}/{str(source_id)}", data=source_options)
        return _resp_to_source(res.json_obj)

    def delete(self, source_id: uuid.UUID) -> AssetCustomSource:
        """
        Deletes a custom asset source from your account.

        :param source_id: Custom asset source id to delete
        :raises AuthError, ClientError, ServerError
        """
        res = self._client.execute("DELETE", f"{self._ENDPOINT}/{source_id}")
        return _resp_to_source(res.json_obj)


def _resp_to_source(json_obj: Any) -> AssetCustomSource:
    source = AssetCustomSource.parse_obj(json_obj)
    if source.icon is not None:
        source.icon = base64.b64decode(source.icon)
    return source
