# generated by datamodel-codegen:
#   filename:  proposed-runzero-api.yml
#   timestamp: 2023-04-28T22:36:38+00:00

from __future__ import annotations

from datetime import datetime
from enum import Enum
from ipaddress import IPv4Address, IPv6Address
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """
    Minimal identifying information with lifecycle metadata
    """

    class Config:
        allow_population_by_field_name = True

    id: UUID = Field(..., example="f6cfb91a-52ea-4a86-bf9a-5a891a26f52b")
    """
    The unique ID of the object
    """
    client_id: UUID = Field(..., alias="clientId", example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    """
    The unique ID of the runZero client/customer account that owns the object
    """
    created_by_id: UUID = Field(..., alias="createdById", example="f6cfb91a-52ea-4a86-bf9a-5a891a26f52b")
    """
    The unique ID of the entity that created the object
    """
    created_at: datetime = Field(..., alias="createdAt", example="2023-03-06T18:14:50.52Z")
    """
    A timestamp indicating creation time of the object
    """
    updated_at: datetime = Field(..., alias="updatedAt", example="2023-03-06T18:14:50.52Z")
    """
    A timestamp indicating last modified time of the object
    """
    destroyed_at: Optional[datetime] = Field(None, alias="destroyedAt", example="2023-03-06T18:14:50.52Z")
    """
    A timestamp indicating deletion time of the object
    """


class BaseCustomIntegration(BaseModel):
    class Config:
        allow_population_by_field_name = True

    name: Optional[str] = Field(None, example="my-custom-integration", regex="^\\S+$")
    """
    The unique name of the custom integration, without spaces.
    """
    icon: Optional[str] = Field(
        None,
        example="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",
    )
    """
    Base64 encoded png with maximum size 256x256 pixels
    """
    description: Optional[str] = Field(None, example="My custom integration description.")
    """
    A text description of the custom integration
    """


class CustomIntegration(BaseCustomIntegration, BaseResponse):
    class Config:
        allow_population_by_field_name = True

    name: str = Field(..., example="my-custom-integration", regex="^\\S+$")
    """
    The unique name of the custom integration, without spaces.
    """


class NewCustomIntegration(BaseCustomIntegration):
    class Config:
        allow_population_by_field_name = True

    name: str = Field(..., example="my-custom-integration", regex="^\\S+$")
    """
    The unique name of the custom integration, without spaces.
    """


class Tag(BaseModel):
    class Config:
        allow_population_by_field_name = True

    __root__: str = Field(..., max_length=1024)


class ImportTask(BaseModel):
    """
    Information which describes the task created when asset data is imported.
    """

    class Config:
        allow_population_by_field_name = True

    name: str = Field(..., example="my import task", max_length=100)
    description: Optional[str] = Field(None, example="importing assets from custom integration A", max_length=1024)
    tags: Optional[List[Tag]] = Field(None, example=["tag1", "tag2"], max_items=100)
    """
    Arbitrary string tag values which are applied to the asset data import task created.
    """


class NewAssetImport(BaseModel):
    """
    Represents a request to import asset data described by the specified custom integration into the specified site.

    Assets will be created new or merged according to merge rules defined by the version of the platform
    you are uploading the asset data file to. Typically, this involves matching network and other unique
    single or grouped properties.

    There is a maximum of 256 custom asset properties that can be applied to any asset. This means
    that, aside from the per-import asset property limit set on ImportAsset, if a new import sets
    different custom properties on the same asset, the new properties are combined with the
    pre-existing ones.

    """

    class Config:
        allow_population_by_field_name = True

    site_id: UUID = Field(..., alias="siteId", example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    """
    The ID of the site assets are to be imported into.
    """
    custom_integration_id: UUID = Field(
        ..., alias="customIntegrationId", example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8"
    )
    """
    The unique ID of the registered custom integration which produced the asset data. Uniqueness is not checked/enforced. See /account/custom-integrations api.
    """
    import_task: ImportTask = Field(..., alias="importTask", title="ImportTask")
    """
    Information which describes the task created when asset data is imported.
    """
    asset_data: bytes = Field(..., alias="assetData")
    """
    A gzip (not .tar.gz) compressed file containing ImportAsset objects. The file data may be a JSON array of
    ImportAsset objects, e.g. [{},{},...] or JSONL format, with a single JSON representation of an ImportAsset
    object on each new line, e.g. {}\n{}\n...

    """


class NetworkInterface(BaseModel):
    class Config:
        allow_population_by_field_name = True

    ipv4_addresses: Optional[List[IPv4Address]] = Field(None, alias="ipv4Addresses", max_items=256)
    """
    Represents IPV4 addresses. Addresses are ordered from most to least likely to uniquely identify the asset.
    """
    ipv6_addresses: Optional[List[IPv6Address]] = Field(None, alias="ipv6Addresses", max_items=100)
    """
    Represents the IPV6 addresses. Addresses are ordered from most to least likely to uniquely identify the asset.
    """
    mac_address: Optional[str] = Field(
        None,
        alias="macAddress",
        example="01:23:45:67:89:0A",
        max_length=23,
        regex=(
            "^([A-Fa-f0-9]{2}:){5}[A-Fa-f0-9]{2}$|^([A-Fa-f0-9]{2}:){7}[A-Fa-f0-9]{2}$|^([A-Fa-f0-9]{2}-){5}[A-Fa-f0-9]{2}$|^([A-Fa-f0-9]{2}-){7}[A-Fa-f0-9]{2}$|^([A-Fa-f0-9]{4}\\.){2}[A-Fa-f0-9]{4}$|^([A-Fa-f0-9]{4}\\.){3}[A-Fa-f0-9]{4}$|^([A-Fa-f0-9]{4}"
            " ){3}[A-Fa-f0-9]{4}$"
        ),
    )
    """
    Represents a MAC address in IEEE 802 MAC/EUI-48, or EUI-64 form in one of the following formats:
      01:23:45:67:89:AB
      01:23:45:67:89:ab:cd:ef
      01-23-45-67-89-ab
      01-23-45-67-89-ab-cd-ef
      0123.4567.89ab
      0123.4567.89ab.cdef
      0123 4567 89ab cdEF

    """


class Hostname(BaseModel):
    class Config:
        allow_population_by_field_name = True

    __root__: str = Field(..., example="host.domain.com", max_length=260)


class CustomAttribute(BaseModel):
    class Config:
        allow_population_by_field_name = True

    __root__: str = Field(..., max_length=1024)


class ImportAsset(BaseModel):
    """
    Represents a custom asset to be created or merged after import.
    """

    class Config:
        allow_population_by_field_name = True

    id: str = Field(..., max_length=1024)
    """
    Any value which can uniquely identify the asset within the custom integration.
    """
    run_zero_id: Optional[UUID] = Field(None, alias="runZeroID", example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    """
    The unique identifier of the runZero asset to merge into.
    """
    network_interfaces: Optional[List[NetworkInterface]] = Field(
        None, alias="networkInterfaces", max_items=256, title="NetworkInterfaces"
    )
    """
    The asset's networking configuration.
    """
    hostnames: Optional[List[Hostname]] = Field(None, max_items=100)
    """
    Represents hostnames the asset is assigned or reachable at. These can be fully-qualified hostnames with the domain name, or a short hostname.
    """
    domain: Optional[str] = Field(None, example="domain.com", max_length=260)
    """
    Represents a single domain name which could be applied to all non-fqdns in the hostnames field.
    """
    first_seen_ts: Optional[datetime] = Field(None, alias="firstSeenTS", example="2023-03-06T18:14:50.52Z")
    """
    Represents the earliest time the asset was seen by the custom integration reporting it, using a date string as defined by RFC 3339, section 5.6.
    """
    os: Optional[str] = Field(None, example="Ubuntu Linux 22.04", max_length=1024)
    """
    The name of the asset's operating system. It is advisable to keep the data clean by normalizing to existing values when possible.
    """
    os_version: Optional[str] = Field(None, alias="osVersion", example="22.04", max_length=1024)
    """
    The version of the asset's operating system. It is advisable to keep the data clean by normalizing to existing values when possible.
    """
    manufacturer: Optional[str] = Field(None, example="Apple Inc.", max_length=1024)
    """
    The manufacturer of the operating system of the asset. It is advisable to keep the data clean by normalizing to existing values when possible.
    """
    model: Optional[str] = Field(None, example="Macbook Air", max_length=1024)
    """
    The hardware model of the asset. It is advisable to keep the data clean by normalizing to existing values when possible.
    """
    tags: Optional[List[Tag]] = Field(None, example=["foo", "key=value"], max_items=100)
    """
    Arbitrary string tags applied to the asset.
    """
    device_type: Optional[str] = Field(None, alias="deviceType", example="Desktop", max_length=1024)
    custom_attributes: Optional[Dict[str, CustomAttribute]] = Field(
        None, alias="customAttributes", title="CustomAttributes"
    )
    """
    Flat map of arbitrary string key/value pairs representing custom attribute data not described in properties above. Note the maximum number of keys and length of values. Additionally, property names may only be 256 characters long.
    """


class ScanFrequency(Enum):
    """
    A string time duration value representing execution frequency, if scheduled to repeat.
    """

    once = "once"
    hourly = "hourly"
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    continuous = "continuous"


class ScanOptions(BaseModel):
    """
    Options which can be set to create or modify a scan.
    """

    class Config:
        allow_population_by_field_name = True

    targets: str = Field(..., example="defaults")
    excludes: Optional[str] = None
    scan_name: Optional[str] = Field(None, alias="scan-name", example="My Scan")
    scan_description: Optional[str] = Field(None, alias="scan-description", example="Scan of Wireless")
    """
    A description of the scan.
    """
    scan_template: Optional[UUID] = Field(None, alias="scan-template", example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    scan_frequency: Optional[ScanFrequency] = Field(None, alias="scan-frequency", example="hour")
    """
    A string time duration value representing execution frequency, if scheduled to repeat.
    """
    scan_start: Optional[str] = Field(None, alias="scan-start", example="0")
    """
    Unix timestamp value indicating when the template was created.
    """
    scan_tags: Optional[str] = Field(None, alias="scan-tags", example="owner=IT location=Texas")
    scan_grace_period: Optional[str] = Field(None, alias="scan-grace-period", example="4")
    agent: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    explorer: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    hosted_zone_id: Optional[str] = Field(None, alias="hosted-zone-id", example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    """
    The string 'auto' will use any available hosted zone. Otherwise, provide the string name (hostedzone1) or UUID (e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8) of a hosted zone.
    """
    hosted_zone_name: Optional[str] = Field(None, alias="hosted-zone-name", example="auto")
    """
    The string 'auto' will use any available hosted zone. Otherwise, provide the string name (hostedzone1) of the hosted zone.
    """
    rate: Optional[str] = Field(None, example="10000")
    max_host_rate: Optional[str] = Field(None, alias="max-host-rate", example="100")
    passes: Optional[str] = Field(None, example="3")
    max_attempts: Optional[str] = Field(None, alias="max-attempts", example="3")
    max_sockets: Optional[str] = Field(None, alias="max-sockets", example="500")
    max_group_size: Optional[str] = Field(None, alias="max-group-size", example="4096")
    max_ttl: Optional[str] = Field(None, alias="max-ttl", example="255")
    tos: Optional[str] = Field(None, example="255")
    tcp_ports: Optional[str] = Field(None, alias="tcp-ports", example="1-1000,5000-6000")
    tcp_excludes: Optional[str] = Field(None, alias="tcp-excludes", example="9500")
    screenshots: Optional[str] = Field(None, example="true")
    nameservers: Optional[str] = Field(None, example="8.8.8.8")
    subnet_ping: Optional[str] = Field(None, alias="subnet-ping", example="true")
    subnet_ping_net_size: Optional[str] = Field(None, alias="subnet-ping-net-size", example="256")
    subnet_ping_probes: Optional[str] = Field(
        None,
        alias="subnet-ping-probes",
        example="arp, echo, syn, connect, netbios, snmp, ntp, sunrpc, ike, openvpn, mdns",
    )
    """
    Optional subnet ping probe list as comma separated strings. The example shows possibilities.
    """
    subnet_ping_sample_rate: Optional[str] = Field(None, alias="subnet-ping-sample-rate", example="3")
    host_ping: Optional[str] = Field(None, alias="host-ping", example="false")
    host_ping_probes: Optional[str] = Field(
        None,
        alias="host-ping-probes",
        example="arp, echo, syn, connect, netbios, snmp, ntp, sunrpc, ike, openvpn, mdns",
    )
    """
    Optional host ping probe list as comma separated strings. The example shows possibilities.
    """
    probes: Optional[str] = Field(
        None,
        example="arp,bacnet,connect,dns,echo,ike,ipmi,mdns,memcache,mssql,natpmp,netbios,pca,rdns,rpcbind,sip,snmp,ssdp,syn,ubnt,wlan-list,wsd",
    )
    """
    Optional probe list, otherwise all probes are used
    """


class ScanTemplateOptions(BaseModel):
    """
    Options which can be set to create a scan template.
    """

    class Config:
        allow_population_by_field_name = True

    name: str = Field(..., example="My Scan Template")
    """
    Name of the template.
    """
    description: Optional[str] = Field(None, example="My Scan Template")
    """
    Description of the template.
    """
    organization_id: UUID = Field(..., example="f6cfb91a-52ea-4a86-bf9a-5a891a26f52b")
    """
    The ID of the organization the template will be created in
    """
    params: Optional[Dict[str, str]] = None
    """
    A number of scan parameter values. Currently there is no authoritative list of acceptable values. See existing templates for examples.
    """
    global_: bool = Field(..., alias="global", example=False)
    """
    Whether the template is globally available to all organizations.
    """
    acl: Dict[str, Any] = Field(..., example={"e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8": "user"})
    """
    A map of IDs to strings which describe how the template may be accessed. Currently there is no authoritative list of acceptable values. See existing templates for examples.
    """


class ScanTemplate(BaseModel):
    """
    A scan task template
    """

    class Config:
        allow_population_by_field_name = True

    id: UUID = Field(..., example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    """
    ID of the template.
    """
    name: Optional[str] = Field(None, example="My Scan Template")
    """
    The name of the template.
    """
    description: Optional[str] = Field(None, example="My Scan Template")
    """
    The description of the template.
    """
    client_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    """
    ID of the account which owns the template.
    """
    organization_id: UUID = Field(..., example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    """
    ID of the organization the template is available in.
    """
    agent_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    """
    ID of the explorer which may execute the template.
    """
    site_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    """
    ID of the site the template is being used in.
    """
    cruncher_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    """
    ID of the runZero cruncher the task is executing on.
    """
    created_at: Optional[int] = Field(None, example=1576300370)
    """
    Unix timestamp value indicating when the template was created.
    """
    created_by: Optional[str] = Field(None, example="user@example.com")
    """
    The username of the account which created the template.
    """
    created_by_user_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    """
    The ID of the account which created the template.
    """
    updated_at: Optional[int] = Field(None, example=1576300370)
    """
    Unix timestamp value indicating when the template was last modified.
    """
    type: Optional[str] = Field(None, example="scan")
    """
    The type of task the template creates.
    """
    status: Optional[str] = Field(None, example="processed")
    """
    The status of the last task using the template.
    """
    error: Optional[str] = Field(None, example="agent unavailable")
    """
    The error message, if any, of the last task using the template.
    """
    params: Optional[Dict[str, str]] = None
    """
    A number of task parameter values. Currently there is no authoritative list of in-use values. See existing templates for examples.
    """
    stats: Optional[Dict[str, Any]] = None
    """
    A map of statistics about the last task executed with the template. Currently there is no authoritative list of in-use values. See existing templates for examples.
    """
    hidden: Optional[bool] = Field(None, example=False)
    """
    A flag indicating whether the item is hidden from common view.
    """
    parent_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    """
    The ID of the parent entity of the task scheduled.
    """
    recur: Optional[bool] = Field(None, example=False)
    """
    A flag representing whether derived tasks are scheduled to repeat.
    """
    recur_frequency: Optional[str] = Field(None, example="hourly")
    """
    A string time duration value representing execution frequency, if scheduled to repeat. You may use
    values including as once, hourly, daily, weekly, monthly, continuous

    """
    start_time: Optional[int] = Field(None, example=1576300370)
    """
    Unix timestamp representing the next execution time.
    """
    recur_last: Optional[int] = Field(None, example=1576300370)
    """
    Unix timestamp representing the last execution if scheduled to repeat.
    """
    recur_next: Optional[int] = Field(None, example=1576300370)
    """
    Unix timestamp representing the next execution if scheduled to repeat.
    """
    recur_last_task_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    """
    The ID of the task that last executed if scheduled to repeat.
    """
    grace_period: Optional[str] = Field(None, example="4")
    """
    Additional time beyond hard expiration deadline by which the task may still be allowed to execute.
    """
    source_id: Optional[str] = Field(None, example="1")
    """
    The numeric ID of the data source, if the task executed with this template is a runZero scan or third party data connection import.
    """
    custom_integration_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    """
    The ID of the custom integration source, if the last task executed with this template was an import of Asset Data.
    """
    template_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    """
    The ID of the template.
    """
    size_site: Optional[int] = Field(None, example=0)
    """
    The size in assets of the site the last task the template was executed against.
    """
    size_data: Optional[int] = Field(None, example=0)
    """
    The total size of result data of the last task the template was used with.
    """
    size_results: Optional[int] = Field(None, example=0)
    """
    The number of results in the last task the template was used with.
    """
    hosted_zone_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    """
    The ID of the hosted zone that ran the last task the template was used with.
    """
    linked_task_count: Optional[int] = Field(None, example=1)
    """
    The number of tasks derived from the template.
    """
    global_: bool = Field(..., alias="global", example=False)
    """
    Whether the template is globally available to all organizations.
    """
    acl: Dict[str, Any] = Field(..., example={"e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8": "user"})
    """
    A map of IDs to strings which describe how the template may be accessed. Currently there is no authoritative list of in-use values. See existing templates for examples.
    """


class Organization(BaseModel):
    class Config:
        allow_population_by_field_name = True

    id: UUID = Field(..., example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    created_at: Optional[int] = Field(None, example=1576300370)
    updated_at: Optional[int] = Field(None, example=1576300370)
    client_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    download_token: Optional[str] = Field(None, example="DT11226D9EEEA2B035D42569585900")
    download_token_created_at: Optional[int] = Field(None, example=1576300370)
    permanent: Optional[bool] = Field(None, example=True)
    name: str = Field(..., example="My Company")
    description: Optional[str] = Field(None, example="All subdivisions of my company")
    inactive: Optional[bool] = Field(None, example=False)
    deactivated_at: Optional[int] = Field(None, example=0)
    service_count: Optional[int] = Field(None, example=10)
    service_count_tcp: Optional[int] = Field(None, example=7)
    service_count_udp: Optional[int] = Field(None, example=1)
    service_count_arp: Optional[int] = Field(None, example=1)
    service_count_icmp: Optional[int] = Field(None, example=1)
    asset_count: Optional[int] = Field(None, example=100)
    export_token: Optional[str] = Field(None, example="ET11226D9EEEA2B035D42569585900")
    export_token_created_at: Optional[int] = Field(None, example=1576300370)
    export_token_last_used_at: Optional[int] = Field(None, example=0)
    export_token_last_used_by: Optional[str] = Field(None, example="127.0.0.1")
    export_token_counter: Optional[int] = Field(None, example=0)
    project: Optional[bool] = Field(None, example=False)
    parent_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    expiration_assets_stale: Optional[int] = Field(None, example=365)
    expiration_assets_offline: Optional[int] = Field(None, example=365)
    expiration_scans: Optional[int] = Field(None, example=365)


class Site(BaseModel):
    class Config:
        allow_population_by_field_name = True

    id: UUID = Field(..., example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    created_at: Optional[int] = Field(None, example=1576300370)
    updated_at: Optional[int] = Field(None, example=1576300370)
    permanent: Optional[bool] = Field(None, example=True)
    name: str = Field(..., example="Primary")
    description: Optional[str] = Field(None, example="Headquarters")
    scope: Optional[str] = Field(None, example="192.168.0.0/24")
    excludes: Optional[str] = Field(None, example="192.168.0.5")
    subnets: Optional[Dict[str, Any]] = None


class SiteOptions(BaseModel):
    class Config:
        allow_population_by_field_name = True

    name: str = Field(..., example="New Site")
    description: Optional[str] = Field(None, example="County Office")
    scope: Optional[str] = Field(None, example="192.168.10.0/24")
    excludes: Optional[str] = Field(None, example="192.168.10.1")


class OrgOptions(BaseModel):
    class Config:
        allow_population_by_field_name = True

    name: Optional[str] = Field(None, example="My Organization")
    description: Optional[str] = Field(None, example="Wobbly Widgets, Inc.")
    export_token: Optional[str] = Field(None, example="ETXXXXXXXXXXXXXXXX")
    parent_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    expiration_assets_stale: Optional[str] = Field(None, example="365", regex="^\\d+$")
    expiration_assets_offline: Optional[str] = Field(None, example="365", regex="^\\d+$")
    expiration_scans: Optional[str] = Field(None, example="365", regex="^\\d+$")


class Agent(BaseModel):
    """
    A deployed service which performs scan tasks.
    Explorers may be referred to by their legacy name, Agents.

    """

    class Config:
        allow_population_by_field_name = True

    id: UUID = Field(..., example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    client_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    organization_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    created_at: Optional[int] = Field(None, example=1576300370)
    updated_at: Optional[int] = Field(None, example=1576300370)
    host_id: Optional[str] = Field(None, example="6f9e6fe52271da70962e007183c5c9c9")
    hub_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    name: Optional[str] = Field(None, example="RUNZERO-AGENT")
    site_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    last_checkin: Optional[int] = Field(None, example=1576300370)
    os: Optional[str] = Field(None, example="Windows")
    arch: Optional[str] = Field(None, example="amd64")
    version: Optional[str] = Field(
        None, example="1.2.3 (build 20191219224016) [fc50c5eefdc3ff5c60533c3c345d14d336396272]"
    )
    external_ip: Optional[str] = Field(None, example="1.1.1.1")
    internal_ip: Optional[str] = Field(None, example="192.168.0.1")
    system_info: Optional[Dict[str, Any]] = None
    connected: Optional[bool] = Field(None, example=True)
    inactive: Optional[bool] = Field(None, example=False)
    deactivated_at: Optional[int] = Field(None, example=0)


class AgentSiteID(BaseModel):
    class Config:
        allow_population_by_field_name = True

    site_id: UUID = Field(..., example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")


class Explorer(BaseModel):
    class Config:
        allow_population_by_field_name = True

    __root__: Agent


class ExplorerSiteID(BaseModel):
    class Config:
        allow_population_by_field_name = True

    __root__: AgentSiteID


class TaskBase(BaseModel):
    """
    All fields of a Task with none required
    """

    class Config:
        allow_population_by_field_name = True

    id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    name: Optional[str] = Field(None, example="Hourly Scan")
    description: Optional[str] = Field(None, example="Scan the headquarters hourly")
    template_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    client_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    organization_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    agent_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    hosted_zone_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    """
    The ID of the Hosted Zone which executes the task. If the

    """
    site_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    cruncher_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    created_at: Optional[int] = Field(None, example=1576300370)
    created_by: Optional[str] = Field(None, example="user@example.com")
    created_by_user_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    custom_integration_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    """
    The ID of the custom integration source, if the last task executed with this template was an import of Asset Data.
    """
    source_id: Optional[int] = Field(None, example=1)
    """
    The numeric ID of the data source, if the task executed with this template is a runZero scan or third party data connection import.
    """
    updated_at: Optional[int] = Field(None, example=1576300370)
    type: Optional[str] = Field(None, example="scan")
    status: Optional[str] = Field(None, example="processed")
    error: Optional[str] = Field(None, example="agent unavailable")
    params: Optional[Dict[str, str]] = None
    stats: Optional[Dict[str, Any]] = None
    hidden: Optional[bool] = Field(None, example=False)
    parent_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    recur: Optional[bool] = Field(None, example=False)
    recur_frequency: Optional[str] = Field(None, example="hourly")
    start_time: Optional[int] = Field(None, example=1576300370)
    recur_last: Optional[int] = Field(None, example=1576300370)
    recur_next: Optional[int] = Field(None, example=1576300370)
    recur_last_task_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")


class Task(TaskBase):
    """
    A task object
    """

    class Config:
        allow_population_by_field_name = True

    id: UUID = Field(..., example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")


class TaskOptions(TaskBase):
    """
    Options which can be set to create or modify a task.
    """

    class Config:
        allow_population_by_field_name = True

    hosted_zone_name: Optional[str] = Field(None, example="auto")
    """
    The string 'auto' will use any available hosted zone. Otherwise, provide the string name (hostedzone1) of the hosted zone.
    """


class HostedZone(BaseModel):
    """
    A hosted service which performs scan tasks. Hosted zones are only available to
    Enterprise customers.

    """

    class Config:
        allow_population_by_field_name = True

    id: UUID = Field(..., example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    """
    The ID of the hosted zone
    """
    name: Optional[str] = Field(None, example="zone1")
    enabled: Optional[bool] = Field(None, example=True)
    """
    Whether the hosted zone is enabled
    """
    updated_at: Optional[datetime] = Field(None, example="2023-03-06T18:14:50.52Z")
    """
    The last modification time of the hosted zone
    """
    processor_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    """
    The processor ID assigned to the hosted zone
    """
    explorers_concurrency: Optional[int] = Field(None, example=0)
    """
    The number of concurrent explorer tasks that can be executed
    """
    explorers_total: Optional[int] = Field(None, example=0)
    """
    The number of explorers available in the zone
    """
    tasks_active: Optional[int] = Field(None, example=0)
    """
    The number of tasks executing in the zone
    """
    tasks_waiting: Optional[int] = Field(None, example=0)
    """
    The number of tasks waiting to execute in the zone
    """
    organization_id: Optional[UUID] = Field(None, example="e77602e0-3fb8-4734-aef9-fbc6fdcb0fa8")
    """
    The ID of the organization the hosted zone is assigned to
    """


class Problem(BaseModel):
    """
    RFC7807 Problem JSON object from https://opensource.zalando.com/restful-api-guidelines/models/problem-1.0.1.yaml without the standard 'type' and 'instance' fields.

    """

    class Config:
        allow_population_by_field_name = True

    title: Optional[str] = Field(None, example="some title for the error situation")
    """
    A short summary of the problem type. Written in English and readable for engineers, usually not suited for non technical stakeholders and not localized.

    """
    status: Optional[int] = Field(None, ge=100, lt=600)
    """
    The HTTP status code generated by the origin server for this occurrence of the problem.

    """
    detail: Optional[str] = Field(None, example="some description for the error situation")
    """
    A human readable explanation specific to this occurrence of the problem that is helpful to locate the problem and give advice on how to proceed. Written in English and readable for engineers, usually not suited for non technical stakeholders and not localized.

    """
