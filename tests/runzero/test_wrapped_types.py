import pytest

from runzero.types import (
    CustomAttribute,
    Hostname,
    ImportAsset,
    Tag,
    ValidationError,
    Vulnerability,
)


def test_wrapped_custom_attribute():
    # testing backwards compat
    attr = CustomAttribute("foo")
    asset = ImportAsset(id="foo", custom_attributes={"some_attr": attr})
    assert len(asset.custom_attributes) == 1

    other_attr = "bar"
    asset = ImportAsset(id="bar", custom_attributes={"some_attr": other_attr})
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


def test_wrapped_vuln():
    vuln = Vulnerability(id="foo")
    asset = ImportAsset(id="foo", vulnerabilities=[vuln])
    assert len(asset.vulnerabilities) == 1
