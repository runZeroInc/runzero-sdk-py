"""
Administrative management of runZero custom integrations, including write operations.

These operations are privileged and require an account token directly or an OAuth key that can generate one.
"""

import base64
import pathlib
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from runzero.client import Client
from runzero.errors import Error
from runzero.types import (
    BaseCustomIntegration,
    CustomIntegration,
    ImportAsset,
    NewCustomIntegration,
)

from ._sdk_source_icon import _PY_ICON_BYTES


class CustomIntegrationAttributeSet(BaseModel):
    """
    A Pydantic-compliant class for marshaling custom attributes.
    """

    attributes: Dict[str, str] = Field(...)


class CRUDAsset(BaseModel):
    """
    A Pydantic-compliant class for marshaling custom assets.
    """

    class Config:
        "Inner config class."

        allow_population_by_field_name = True

    id: str = Field(..., max_length=1024)
    macs: Optional[List[str]] = Field(None)
    addresses: Optional[List[str]] = Field(None)
    addresses_extra: Optional[List[str]] = Field(None)
    hostnames: Optional[List[str]] = Field(None)
    domains: Optional[List[str]] = Field(None)
    first_seen: Optional[int] = Field(None)
    os: Optional[str] = Field(None, max_length=1024)
    os_vendor: Optional[str] = Field(None, max_length=1024)
    os_version: Optional[str] = Field(None, max_length=1024)
    hw: Optional[str] = Field(None, max_length=1024)
    hw_vendor: Optional[str] = Field(None, max_length=1024)
    tags: Optional[str] = Field(None, max_length=1024)
    device_type: Optional[str] = Field(None, max_length=1024)
    custom_attributes: Optional[Dict[str, str]] = Field(None)

    def merge_import_asset(self, import_asset: ImportAsset) -> None:  # pylint: disable=too-many-statements
        """
        Merge an existing ImportAsset with this CRUD asset.
        """
        self.id = import_asset.id
        self.macs = []
        self.addresses = []
        self.addresses_extra = []
        self.hostnames = [hostname.__root__ for hostname in import_asset.hostnames] if import_asset.hostnames else []
        self.domains = [import_asset.domain] if import_asset.domain else []
        self.first_seen = 0
        self.os = import_asset.os or ""
        self.os_vendor = import_asset.manufacturer or ""
        self.os_version = ""
        self.hw = import_asset.model or ""
        self.hw_vendor = ""
        self.tags = ""
        self.device_type = import_asset.device_type or ""
        self.custom_attributes = {}

        if import_asset.first_seen_ts is not None:
            self.first_seen = int(import_asset.first_seen_ts.timestamp())

        if import_asset.tags:
            self.tags = "\t".join(tag.__root__ for tag in import_asset.tags)

        if import_asset.custom_attributes is not None:
            for key, value in import_asset.custom_attributes.items():
                if key == "macAddresses":
                    self.macs = value.split("\t")

                elif key == "ipAddresses":
                    self.addresses = value.split("\t")

                elif key == "ipAddressesExtra":
                    self.addresses_extra = value.split("\t")

                elif key == "hostnames":
                    self.hostnames = value.split("\t")

                elif key == "domain":
                    if self.domains is None:
                        self.domains = []
                    self.domains.append(value)

                elif key == "os":
                    self.os = value

                elif key == "osVersion":
                    self.os_version = value

                elif key == "manufacturer":
                    self.hw_vendor = value

                elif key == "model":
                    self.hw = value

                elif key == "tags":
                    if self.tags is None:
                        self.tags = value
                    else:
                        self.tags = self.tags + " " + value

                elif key == "deviceType":
                    self.device_type = value

                elif key in ("ownedBy", "runZeroID", "_services", "_software", "_vulnerabilities"):
                    # Skip; we don't support these yet.
                    continue

                elif key in ("firstSeenTS", "lastSeenTS"):
                    # Skip; these are set directly on the import asset.
                    continue

                else:
                    self.custom_attributes[key] = value


class CRUDImportAsset(BaseModel):
    """
    A wrapper class for importing assets via CRUD.
    """

    asset: CRUDAsset


class CustomIntegrationAssetAdmin:
    """Allows administration of custom integration-related features of assets.

    This allows for assets to be created via a custom integration, without creating a runZero
    import task, and for setting of attributes on assets using this custom integration.

    :param client: A handle to the :class:`runzero.Client` which manages interactions
        with the runZero server.
    """

    def __init__(self, client: Client, integration_id: uuid.UUID) -> None:
        """Constructor methods."""
        self._client = client
        self._id = integration_id

    def create_asset(self, org_id: uuid.UUID, site_id: uuid.UUID, asset: ImportAsset) -> uuid.UUID:
        """Create a new asset in the specified organization and site, using this custom integration..

        Note that not all fields of an :class:`ImportAsset` can be used when creating an asset directly.

        :param org_id: organization id
        :param site_id: site id
        :param asset: a description of the asset to be created:

        :returns: A UUID identifying the new asset in runZero.
        :raises: AuthError, ClientError, ServerError
        """

        crud_asset = CRUDAsset(
            id=asset.id,
            macs=[],
            addresses=[],
            addresses_extra=[],
            hostnames=[],
            domains=[],
            first_seen=0,
            os="",
            os_vendor="",
            hw="",
            tags="",
            device_type="",
            custom_attributes={},
        )
        crud_asset.merge_import_asset(asset)

        res = self._client.execute(
            "POST",
            f"api/v1.0/org/custom-integrations/{self._id}/asset",
            params={"_oid": str(org_id), "site": str(site_id)},
            data=CRUDImportAsset(asset=crud_asset),
        )
        return res.json_obj["asset_id"]

    def bulk_update_custom_attributes(
        self,
        org_id: uuid.UUID,
        search: str,
        attributes: Dict[str, str],
        site: Optional[uuid.UUID] = None,
        limit: int = 0,
    ) -> int:
        """
        Adds, deletes, and updates custom integration attributes on assets matching the given search.

        :param org_id: organization id
        :param search: a search query to locate assets to update
        :param attributes: a dictionary of key-value pairs to update; empty values delete attributes
        :param site: limit the search to a given site
        :param limit: limit the number of query results

        :returns: An integer indicating the number of assets updated
        :raises: AuthError, ClientError, ServerError
        """

        res = self._client.execute(
            "PATCH",
            f"api/v1.0/org/custom-integrations/{self._id}/attributes",
            params={
                "_oid": org_id,
                "site": site or "",
                "limit": limit or 0,
                "search": search,
            },
            data=CustomIntegrationAttributeSet(attributes=attributes),
        )

        return res.json_obj.get("updated", 0)

    def update_custom_attributes(self, org_id: uuid.UUID, asset_id: uuid.UUID, attributes: Dict[str, str]) -> int:
        """
        Adds, deletes, or updates custom integration attributes on a specific asset.

        :param org_id: organization id
        :param asset_id: the asset to update
        :param attributes: a dictionary of key-value pairs to update; empty values delete attributes

        :returns: An integer indicating the number of assets updated
        :raises: AuthError, ClientError, ServerError
        """

        res = self._client.execute(
            "PATCH",
            f"api/v1.0/org/assets/{asset_id}/custom-integrations/{self._id}/attributes",
            params={"_oid": org_id, "limit": 0},
            data=CustomIntegrationAttributeSet(attributes=attributes),
        )

        return res.json_obj.get("updated", 0)


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

    def get_asset_admin_handle(self, custom_integration_id: uuid.UUID) -> Optional[CustomIntegrationAssetAdmin]:
        """
        Gets a CustomIntegrationAdmin object to manipulate assets related to the given integration.

        :param custom_integration_id: The ID of the custom integration.

        :raises: AuthError, ClientError, ServerError
            ValueError if neither custom_integration_id nor name are provided.
        :returns: The matching CustomIntegrationAssetAdmin or None
        """

        if self.get(custom_integration_id=custom_integration_id) is not None:
            return CustomIntegrationAssetAdmin(self._client, custom_integration_id)

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
