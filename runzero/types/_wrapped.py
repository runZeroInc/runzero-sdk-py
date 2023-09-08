"""Wrapped types are subclassed, method-free pydantic data types that expose
additional fields or replace existing fields to occlude API detail.

These types may be declared here, and not in modules that expose functionality,
when there is no constructor, method, or additional decision code on or related
to the class. Every type is to be a pure Pydantic data classes with validations.

Each class should have a non-docstring comment in it describing why the REST type
was insufficient.
"""

from typing import Any, Dict, Iterable, Optional

# Note: `validator` has been replaced with `field_validator` in v2+
from pydantic import Field, ValidationError, validator

from ._data_models_gen import CustomAttribute as RESTCustomAttribute
from ._data_models_gen import CustomIntegration as RESTCustomIntegration
from ._data_models_gen import Hostname as RESTHostname
from ._data_models_gen import ImportAsset as RESTImportAsset
from ._data_models_gen import ScanOptions as RESTScanOptions
from ._data_models_gen import ScanTemplate as RESTScanTemplate
from ._data_models_gen import ScanTemplateOptions as RESTScanTemplateOptions
from ._data_models_gen import Tag as RESTTag


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


class CustomAttribute(RESTCustomAttribute):
    """
    CustomAttribute is a string key / value pair from an external custom asset data source.
    """

    def __init__(self, attr: str):
        super().__init__(__root__=attr)


class ImportAsset(RESTImportAsset):
    """
    Represents a custom asset to be created or merged after import.
    """

    __MAX_ATTRS = 1024
    __MAX_ATTR_KEY_LEN = 256

    def __int__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    @validator("custom_attributes")
    def custom_attributes_length(  # pylint: disable=E0213
        cls, attrs: Dict[str, CustomAttribute]
    ) -> Dict[str, CustomAttribute]:
        """
        Validates that the length of the dict used for `custom_attributes` does not exceed a length of 256 items and
        that each key in that dict does not itself exceed a length of 256 characters.
        """
        if len(attrs) > cls.__MAX_ATTRS:
            raise ValidationError(
                f"custom attributes exceeds length of 256 with length of {len(attrs)}",
                ImportAsset,
            )
        for k in attrs.keys():
            if len(k) > cls.__MAX_ATTR_KEY_LEN:
                raise ValidationError(
                    f"key {k[:25]}... in custom_attributes exceeds maximum length of 256 with length of {len(k)}",
                    ImportAsset,
                )
        return attrs


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
