"""Wrapped types are subclassed, method-free pydantic data types that expose
additional fields or replace existing fields to occlude API detail.

These types may be declared here, and not in modules that expose functionality,
when there is no constructor, method, or additional decision code on or related
to the class. Every type is to be a pure Pydantic data classes with validations.

Each class should have a non-docstring comment in it describing why the REST type
was insufficient.
"""

from typing import Optional

from pydantic import Field

from ._data_models_gen import AssetCustomSource as RESTAssetCustomSource


class AssetCustomSource(RESTAssetCustomSource):
    """AssetCustomSource represents a custom asset data source for custom integrations use"""

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
