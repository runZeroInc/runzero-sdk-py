"""Wrapped types are subclassed, method-free pydantic data types that expose
additional fields or replace existing fields to occlude API detail.

These types may be declared here, and not in modules that expose functionality,
when there is no constructor, method, or additional decision code on or related
to the class. Every type is to be a pure Pydantic data classes with validations.

Each class should have a non-docstring comment in it describing why the REST type
was insufficient.
"""

from ipaddress import IPv4Address, IPv6Address, ip_address
from typing import Any, Dict, Iterable, List, Optional, Union
from warnings import warn

# Note: `validator` has been replaced with `field_validator` in v2+
from pydantic import BaseModel, Field, ValidationError, validator

from ._data_models_gen import CustomIntegration as RESTCustomIntegration
from ._data_models_gen import Hostname as RESTHostname
from ._data_models_gen import ImportAsset as RESTImportAsset
from ._data_models_gen import NetworkInterface as RESTNetworkInterface
from ._data_models_gen import ScanOptions as RESTScanOptions
from ._data_models_gen import ScanTemplate as RESTScanTemplate
from ._data_models_gen import ScanTemplateOptions as RESTScanTemplateOptions
from ._data_models_gen import Software as RESTSoftware
from ._data_models_gen import Tag as RESTTag
from ._data_models_gen import Vulnerability as RESTVulnerability


class CustomIntegration(RESTCustomIntegration):
    """CustomIntegration represents a custom asset data source for custom integrations use"""

    # The REST API uses base-64 encoded strings, but inside this SDK
    # we want always use bytes and hide the transport encoding.
    # Note that it's unsafe to override types in a subclass
    # according to mypy - it would be better to compose than
    # inherit. But we are wrapping our own API :)

    icon: Optional[bytes] = Field(  # type: ignore[assignment]
        None,
        max_length=200000,
    )
    """
    bytes of png formatted image with maximum size 32x32 pixels
    """


class __CustomAttribute(BaseModel):  # pylint: disable=C0103
    """
    __RESTCustomAttribute is vestigial from an earlier version of the SDK and is being kept here for backwards
    compatability purposes. This will be removed as part of the SDK 1.0 release.
    """

    class Config:
        """Config for pydantic model"""

        allow_population_by_field_name = True

    __root__: str = Field(..., max_length=1024)


class CustomAttribute(__CustomAttribute):
    """
    :DEPRECATION NOTICE:
    This class is deprecated and will be removed in the 1.0 release of the SDK.
    You can now use a Dict[str, str] directly when setting the custom_attributes property.
    This class is replaced by simply using a string.

    CustomAttribute is a string key / value pair from an external custom asset data source.
    """

    def __init__(self, attr: str):
        warn(
            f"{self.__class__.__name__} is deprecated and will be removed in the 1.0 release of the SDK. You can now"
            " directly use a string instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(__root__=attr)


class Hostname(RESTHostname):
    """
    Hostname the dns name the asset is assigned or reachable at.

    This can be a fully-qualified hostname with the domain name, or
    a short hostname.
    """

    def __init__(self, hostname: str):
        super().__init__(__root__=hostname)


class Tag(RESTTag):
    """
    Tag is an arbitrary string classifier applied to the asset.
    """

    def __init__(self, tag: str):
        super().__init__(__root__=tag)


class ImportAsset(RESTImportAsset):
    """
    Represents a custom asset to be created or merged after import.
    """

    __MAX_ATTRS = 1024
    __MAX_ATTR_KEY_LEN = 256
    __MAX_ATTR_VAL_LEN = 1024

    def __int__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    @validator("hostnames", pre=True)
    def _hostnames_str_conversion(cls, hosts: List[Union[str, Hostname]]) -> List[Hostname]:  # pylint: disable=E0213
        """
        Handles conversion of strings to Hostname class for user convenience.

        Ultimately, we want to give users type safety but without burdening them with over-zealous runtime type checks.
        """
        result: List[Hostname] = []

        for host in hosts:
            if isinstance(host, str):
                host = Hostname(host)
            result.append(host)

        return result

    @validator("tags", pre=True)
    def _tag_str_conversion(cls, tags: List[Union[str, Tag]]) -> List[Tag]:  # pylint: disable=E0213
        """
        Handles conversion of strings to Tags for user convenience.

        Ultimately, we want to give users type safety without burdening them with over-zealous runtime type checks.
        """
        result: List[Tag] = []

        for tag in tags:
            if isinstance(tag, str):
                tag = Tag(tag)
            result.append(tag)

        return result

    @validator("custom_attributes", pre=True)
    def _custom_attributes_length(  # pylint: disable=E0213
        cls, attrs: Dict[str, Union[CustomAttribute, str]]
    ) -> Dict[str, str]:
        """
        Validates that the length of the dict used for `custom_attributes` does not exceed a length of 256 items and
        that each key in that dict does not itself exceed a length of 256 characters.
        """
        if len(attrs) > cls.__MAX_ATTRS:
            raise ValidationError(
                f"custom attributes exceeds length of 256 with length of {len(attrs)}",
                ImportAsset,
            )

        # store for return value after type casting to handle CustomAttribute instances
        processed_attrs: Dict[str, str] = {}

        for k, val in attrs.items():
            if len(k) > cls.__MAX_ATTR_KEY_LEN:
                raise ValidationError(
                    f"key {k[:25]}... in custom_attributes exceeds maximum length of 256 with length of {len(k)}",
                    ImportAsset,
                )

            # CustomAttribute used to be the required type for the custom attributes value field
            # Now we use strings - but still support CustomAttribute for backwards compatability
            # Thus we need to cast any CustomAttribute() to a string because the wrapped type uses strings
            if isinstance(val, CustomAttribute):
                val = val.__root__
                attrs[k] = val
            if len(val) > cls.__MAX_ATTR_VAL_LEN:
                raise ValidationError(
                    f"key {k[:25]}... in custom_attributes has a value which the exceeds maximum length of 1024 with"
                    f" length of {len(str(val))}",
                    ImportAsset,
                )
            processed_attrs[k] = val

        return processed_attrs


class NetworkInterface(RESTNetworkInterface):
    """
    Represents the Network Interface of an asset to be imported.
    """

    def __int__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    @validator("ipv4_addresses", pre=True)
    def _ipv4_str_conversion(  # pylint: disable=E0213
        cls, ipv4s: Optional[List[Union[str, IPv4Address]]]
    ) -> Optional[List[IPv4Address]]:
        """
        Converts strings to IPv4Addresses which allows the user convenience of just passing in a string
        """
        if ipv4s is None:
            return None

        result: List[IPv4Address] = []

        for ipv4 in ipv4s:
            if isinstance(ipv4, str):
                ipv4 = IPv4Address(ipv4)
            result.append(ipv4)

        return result

    @validator("ipv6_addresses", pre=True)
    def _ipv6_str_conversion(  # pylint: disable=E0213
        cls, ipv6s: Optional[List[Union[str, IPv6Address]]]
    ) -> Optional[List[IPv6Address]]:
        """
        Converts strings to IPv6Addresses which allows the user convenience of just passing in a string
        """
        if ipv6s is None:
            return None

        result: List[IPv6Address] = []

        for ipv6 in ipv6s:
            if isinstance(ipv6, str):
                ipv6 = IPv6Address(ipv6)
            result.append(ipv6)

        return result


class ScanOptions(RESTScanOptions):
    """Options which can be set to create or modify a scan."""

    # enable kebab-case json response
    def json(self, *args: Iterable[Any], **kwargs: Any) -> str:
        """Ensure kebab-case is kept when converting to JSON"""
        kwargs.setdefault("by_alias", True)
        return super().json(*args, **kwargs)


class ScanTemplate(RESTScanTemplate):
    """A scan template object"""

    # enable kebab-case json response
    def json(self, *args: Iterable[Any], **kwargs: Any) -> str:
        """Ensure kebab-case is kept when converting to JSON"""
        kwargs.setdefault("by_alias", True)
        return super().json(*args, **kwargs)


class ScanTemplateOptions(RESTScanTemplateOptions):
    """Options which can be set to create or modify a scan template."""

    # enable kebab-case json response
    def json(self, *args: Iterable[Any], **kwargs: Any) -> str:
        """Ensure kebab-case is kept when converting to JSON"""
        kwargs.setdefault("by_alias", True)
        return super().json(*args, **kwargs)


class Software(RESTSoftware):
    """
    Represents a piece of installed software on a particular asset.
    """

    __MAX_ATTRS = 1024
    __MAX_ATTR_KEY_LEN = 256
    __MAX_ATTR_VAL_LEN = 1024

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    @validator("service_transport", pre=True)
    def _lower_case_service_transport(cls, attr: str) -> str:  # pylint: disable=E0213
        # disabled pylint because @validator turns the method into a classmethod
        """
        This simply lower-cases transport name for convenience
        """
        return attr.lower()

    @validator("cpe23", pre=True)
    def _lower_case_cpe(cls, attr: str) -> str:  # pylint: disable=E0213
        # disabled pylint because @validator turns the method into a classmethod
        """
        This simply lower-cases the cpe23 string given by the user so that they don't get punished for overly pedantic
        regex.
        """
        return attr.lower()

    @validator("service_address", pre=True)
    def _service_address_str_conversion(  # pylint: disable=E0213
        cls, addr: Union[str, IPv4Address, IPv6Address]
    ) -> Union[IPv4Address, IPv6Address]:
        """
        This gives the user the convenience of passing in a valid ipv4/ipv6 as a string and doing type conversion
        """
        if isinstance(addr, str):
            addr = ip_address(addr)
        return addr

    @validator("custom_attributes", pre=True)
    def _custom_attributes_length(  # pylint: disable=E0213
        cls, attrs: Dict[str, Union[CustomAttribute, str]]
    ) -> Dict[str, str]:
        # disabled pylint because @validator turns the method into a classmethod
        """
        Validates the following:
        - that the length of the dict used for `custom_attributes` does not exceed a length of 256 items
        - that each key in that dict does not exceed a length of 256 characters
        - that the length of each value does not exceed a length of 1024 characters
        """
        if len(attrs) > cls.__MAX_ATTRS:
            raise ValidationError(
                f"custom attributes exceeds length of 256 with length of {len(attrs)}",
                ImportAsset,
            )

        # store for return value after type casting to handle CustomAttribute instances
        processed_attrs: Dict[str, str] = {}

        for k, val in attrs.items():
            if len(k) > cls.__MAX_ATTR_KEY_LEN:
                raise ValidationError(
                    f"key {k[:25]}... in custom_attributes exceeds maximum length of 256 with length of {len(k)}",
                    ImportAsset,
                )

            # CustomAttribute used to be the required type for the custom attributes value field
            # Now we use strings - but still support CustomAttribute for backwards compatability
            # Thus we need to cast any CustomAttribute() to a string because the wrapped type uses strings
            if isinstance(val, CustomAttribute):
                val = val.__root__
                attrs[k] = val
            if len(val) > cls.__MAX_ATTR_VAL_LEN:
                raise ValidationError(
                    f"key {k[:25]}... in custom_attributes has a value which the exceeds maximum length of 1024 with"
                    f" length of {len(str(val))}",
                    ImportAsset,
                )
            processed_attrs[k] = val

        return processed_attrs


class Vulnerability(RESTVulnerability):
    """
    Represents a vulnerability present on a particular asset.
    """

    __MAX_ATTRS = 1024
    __MAX_ATTR_KEY_LEN = 256
    __MAX_ATTR_VAL_LEN = 1024

    def __int__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    @validator("service_transport", pre=True)
    def _lower_case_service_transport(cls, attr: str) -> str:  # pylint: disable=E0213
        # disabled pylint because @validator turns the method into a classmethod
        """
        This simply lower-cases transport name for convenience
        """
        return attr.lower()

    @validator("cpe23", pre=True)
    def _lower_case_cpe(cls, attr: str) -> str:  # pylint: disable=E0213
        # disabled pylint because @validator turns the method into a classmethod
        """
        This simply lower-cases the cpe23 string given by the user so that they don't get punished for overly pedantic
        regex.
        """
        return attr.lower()

    @validator("cve", pre=True)
    def _upper_case_cve(cls, attr: str) -> str:  # pylint: disable=E0213
        # disabled pylint because @validator turns the method into a classmethod
        """
        This simply upper-cases the string given by the user so that they don't get punished by overly pedantic regex.
        """
        return attr.upper()

    @validator("service_address", pre=True)
    def _service_address_str_conversion(  # pylint: disable=E0213
        cls, addr: Union[str, IPv4Address, IPv6Address]
    ) -> Union[IPv4Address, IPv6Address]:
        """
        This gives the user the convenience of passing in a valid ipv4/ipv6 as a string and doing type conversion
        """
        if isinstance(addr, str):
            addr = ip_address(addr)
        return addr

    @validator("custom_attributes", pre=True)
    def _custom_attributes_length(  # pylint: disable=E0213
        cls, attrs: Dict[str, Union[CustomAttribute, str]]
    ) -> Dict[str, str]:
        # disabled pylint because @validator turns the method into a classmethod
        """
        Validates the following:
        - that the length of the dict used for `custom_attributes` does not exceed a length of 256 items
        - that each key in that dict does not exceed a length of 256 characters
        - that the length of each value does not exceed a length of 1024 characters
        """
        if len(attrs) > cls.__MAX_ATTRS:
            raise ValidationError(
                f"custom attributes exceeds length of 256 with length of {len(attrs)}",
                ImportAsset,
            )

        # store for return value after type casting to handle CustomAttribute instances
        processed_attrs: Dict[str, str] = {}

        for k, val in attrs.items():
            if len(k) > cls.__MAX_ATTR_KEY_LEN:
                raise ValidationError(
                    f"key {k[:25]}... in custom_attributes exceeds maximum length of 256 with length of {len(k)}",
                    ImportAsset,
                )

            # CustomAttribute used to be the required type for the custom attributes value field
            # Now we use strings - but still support CustomAttribute for backwards compatability
            # Thus we need to cast any CustomAttribute() to a string because the wrapped type uses strings
            if isinstance(val, CustomAttribute):
                val = val.__root__
                attrs[k] = val
            if len(val) > cls.__MAX_ATTR_VAL_LEN:
                raise ValidationError(
                    f"key {k[:25]}... in custom_attributes has a value which the exceeds maximum length of 1024 with"
                    f" length of {len(str(val))}",
                    ImportAsset,
                )
            processed_attrs[k] = val

        return processed_attrs
