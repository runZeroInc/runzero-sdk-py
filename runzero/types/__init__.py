"""
types provides the Pydantic data model representations of the runZero Platform
API schema, as well as other data types which wrap looser runZero API data.

Public, SDK-supported runZero API types contained inside this package are made
available here. Not all objects in the private module, which is generated from
OpenAPI specs, are usable in this project today.
"""

from ipaddress import AddressValueError, IPv4Address, IPv6Address

from pydantic import ValidationError

from runzero.types._data_models_gen import Agent as Explorer
from runzero.types._data_models_gen import AgentSiteID as ExplorerSiteID
from runzero.types._data_models_gen import (
    BaseCustomIntegration,
    HostedZone,
    ImportTask,
    NewAssetImport,
    NewCustomIntegration,
    Organization,
    OrgOptions,
    Problem,
    Site,
    SiteOptions,
    Task,
    TaskOptions,
)
from runzero.types._rate_limit_information import RateLimitInformation
from runzero.types._wrapped import (
    CustomAttribute,
    CustomIntegration,
    Hostname,
    ImportAsset,
    NetworkInterface,
    ScanOptions,
    ScanTemplate,
    ScanTemplateOptions,
    Software,
    Tag,
    Vulnerability,
)

__all__ = [
    "AddressValueError",
    "BaseCustomIntegration",
    "CustomAttribute",
    "CustomIntegration",
    "Explorer",
    "ExplorerSiteID",
    "HostedZone",
    "Hostname",
    "IPv4Address",
    "IPv6Address",
    "ImportAsset",
    "ImportTask",
    "NetworkInterface",
    "NewAssetImport",
    "NewCustomIntegration",
    "Organization",
    "OrgOptions",
    "Problem",
    "RateLimitInformation",
    "ScanOptions",
    "ScanTemplate",
    "ScanTemplateOptions",
    "Software",
    "Site",
    "SiteOptions",
    "Tag",
    "Task",
    "TaskOptions",
    "ValidationError",
    "Vulnerability",
]
