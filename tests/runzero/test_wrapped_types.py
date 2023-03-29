import pytest

# TODO: we should be able to use the runzero.types.ValidationError for this
from pydantic import ValidationError

from runzero.types import CustomAttribute, Hostname, ImportAsset, Tag


def test_wrapped_custom_attribute():
    attr = CustomAttribute("foo")
    asset = ImportAsset(id="foo", customAttributes={"some_attr": attr})
    assert len(asset.custom_attributes) == 1


def test_wrapped_custom_attribute_invalid():
    # this string will be too long for the limit of the underlying type
    invalid = "foo" * 1000
    with pytest.raises(ValidationError):
        CustomAttribute(invalid)


def test_wrapped_tag():
    tag1 = Tag("some tag")
    tag2 = Tag("some other tag")
    asset = ImportAsset(id="foo", tags=[tag1, tag2])
    assert len(asset.tags) == 2


def test_wrapped_tag_invalid():
    # this string will be too long for the limit of the underlying type
    invalid = "foo" * 1000
    with pytest.raises(ValidationError):
        Tag(invalid)


def test_wrapped_hostname():
    host = Hostname("test.domain.com")
    asset = ImportAsset(id="foo", hostnames=[host])
    assert len(asset.hostnames) == 1


def test_wrapped_hostname_invalid():
    # this string will be too long for the limit of the underlying type
    invalid = "x" * 1000
    with pytest.raises(ValidationError):
        Hostname(invalid)
