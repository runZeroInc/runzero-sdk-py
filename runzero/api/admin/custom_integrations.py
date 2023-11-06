"""
Administrative management of runZero custom integrations, including write operations.

These operations are privileged and require an account token directly or an OAuth key that can generate one.
"""

import base64
import pathlib
import uuid
from pathlib import Path
from typing import Any, List, Optional, Union

from runzero.client import Client
from runzero.errors import Error
from runzero.types import BaseCustomIntegration, CustomIntegration, NewCustomIntegration

from ._sdk_source_icon import _PY_ICON_BYTES


class CustomIntegrationsAdmin:
    """Full Management of custom integrations.

    Custom integrations are descriptive registered associations between integrations of data and
    assets imported which are associated with those integrations.

    This is a superset of operations available in runzero.custom_integrations.CustomIntegrations
    which allows only read operations.

    :param client: A handle to the :class:`runzero.Client` which manages interactions
        with the runZero server.
    """

    _ENDPOINT = "api/v1.0/account/custom-integrations"

    PYTHON_ICON = _PY_ICON_BYTES
    """A default icon representing a custom integration defined via this Python SDK."""

    def __init__(self, client: Client):
        """Constructor method"""
        self._client = client

    def get_all(self) -> List[CustomIntegration]:
        """
        Lists all custom integrations available to your account.

        :returns: List of custom integrations
        :raises: AuthError, ClientError, ServerError
        """
        res = self._client.execute("GET", self._ENDPOINT)
        result: List[CustomIntegration] = []
        for src in res.json_obj:
            result.append(_resp_to_source(src))
        return result

    def get(
        self, name: Optional[str] = None, custom_integration_id: Optional[uuid.UUID] = None
    ) -> Optional[CustomIntegration]:
        """
        Retrieves runZero custom integrations with either the matching ID or Name.

        :param name: Optional, name of the custom integration to retrieve
        :param custom_integration_id: Optional, the id of the custom integration to retrieve

        :raises: AuthError, ClientError, ServerError
            ValueError if neither custom_integration_id nor name are provided.
        :returns: The matching CustomIntegration or None
        """
        if name is None and custom_integration_id is None:
            raise ValueError("must provide custom_integration_id or source name")
        if custom_integration_id is not None:
            res = self._client.execute("GET", f"{self._ENDPOINT}/{custom_integration_id}")
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
    ) -> CustomIntegration:
        """
        Creates a new custom integration.

        :param name: Name of custom integration to be created in to your account. The
            name may not contain spaces, tabs, or other whitespace
        :param description: Optional description of custom integration to be created
        :param icon: Optional file path to, or bytes of icon data. The icon must be
            a png formatted image with a maximum size of 32x32. Icon format
            is validated by the server. The default value assigns your custom
            data source the Python logo to indicate it was created by this SDK.
            Use None to have the server choose the default custom integration logo,
            a grey runZero logo

        :returns: CustomIntegration created
        :raises: AuthError, ClientError, ServerError
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
        req = NewCustomIntegration(name=name, description=description, icon=icon)
        res = self._client.execute("POST", self._ENDPOINT, data=req)
        return _resp_to_source(res.json_obj)

    def update(self, custom_integration_id: uuid.UUID, source_options: BaseCustomIntegration) -> CustomIntegration:
        """
        Updates a custom integration associated with your account.

        :param custom_integration_id: custom integration with updated values
        :param source_options: custom integration request values to update

        :returns: CustomIntegration updated
        :raises: AuthError, ClientError, ServerError
        """
        res = self._client.execute("PATCH", f"{self._ENDPOINT}/{custom_integration_id}", data=source_options)
        return _resp_to_source(res.json_obj)

    def delete(self, custom_integration_id: uuid.UUID) -> CustomIntegration:
        """
        Deletes a custom integration from your account.

        :param custom_integration_id: custom integration id to delete

        :returns: CustomIntegration deleted
        :raises: AuthError, ClientError, ServerError
        """
        res = self._client.execute("DELETE", f"{self._ENDPOINT}/{custom_integration_id}")
        return _resp_to_source(res.json_obj)


def _resp_to_source(json_obj: Any) -> CustomIntegration:
    source = CustomIntegration.parse_obj(json_obj)
    if source.icon is not None:
        source.icon = base64.b64decode(source.icon)
    return source
