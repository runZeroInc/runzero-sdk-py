import pytest

from runzero.types import (
    AddressValueError,
    CustomAttribute,
    ImportAsset,
    IPv4Address,
    IPv6Address,
    NetworkInterface,
    ValidationError,
)


def test_network_interface_validation_empty():
    """
    This test ensures that an empty NetworkInterface can be created without error
    """
    ni = NetworkInterface()
    assert ni.mac_address is None
    assert ni.ipv4_addresses is None
    assert ni.ipv6_addresses is None


def test_network_interface_all_values_optional():
    """
    This test ensures that all values for a network interface are optional
    """
    ni = NetworkInterface(mac_address=None, ipv4_addresses=None, ipv6_addresses=None)
    assert ni.mac_address is None
    assert ni.ipv4_addresses is None
    assert ni.ipv6_addresses is None


def test_network_interface_invalid_fields():
    """
    This test ensures that empty values cannot be used without error
    """
    with pytest.raises(ValidationError):
        NetworkInterface(mac_address="")

    with pytest.raises(AddressValueError):
        NetworkInterface(ipv4_addresses=[IPv4Address("")])

    with pytest.raises(AddressValueError):
        NetworkInterface(ipv6_addresses=[IPv6Address("")])


def test_custom_attributes_length_limit():
    """
    This test ensures that `custom_attributes` have a length limit of 1024 per asset
    """
    valid_attributes = {f"foo-{n}": f"{n}" for n in range(1024)}
    invalid_attributes = {f"foo-{n}": f"{n}" for n in range(1025)}

    asset = ImportAsset(id="valid", custom_attributes=valid_attributes)
    assert len(asset.custom_attributes) == 1024

    with pytest.raises(ValidationError):
        ImportAsset(id="invalid", custom_attributes=invalid_attributes)


def test_custom_attributes_key_length_limit():
    """
    This test ensures that the keys in the `custom_attributes` have a length limit of 256
    """
    valid_attributes = {"f" * 256: "valid-test"}
    invalid_attributes = {"f" * 257: "invalid-test"}

    asset = ImportAsset(id="valid", custom_attributes=valid_attributes)
    assert len(asset.custom_attributes) == 1

    with pytest.raises(ValidationError):
        ImportAsset(id="invalid", custom_attributes=invalid_attributes)


def test_custom_attributes_value_length_limit():
    """
    This test ensures that the values in the `custom_attributes` have a length limit of 1024
    """
    valid_attributes = {"valid-test": CustomAttribute("f" * 1024)}
    with pytest.raises(ValidationError):
        # CustomAttributes should already enforce a max length of 1024
        CustomAttribute("f" * 1025)

    # However - it's still possible for a user to utilize a raw Dict[str, str] in its place
    invalid_attributes = {"invalid-test": "f" * 1025}

    asset = ImportAsset(id="valid", custom_attributes=valid_attributes)
    assert len(asset.custom_attributes) == 1

    with pytest.raises(ValidationError):
        # thus, the ImportAsset itself should enforce this
        ImportAsset(id="invalid", custom_attributes=invalid_attributes)
