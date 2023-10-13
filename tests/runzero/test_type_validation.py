import pytest

from runzero.types import (
    AddressValueError,
    CustomAttribute,
    Hostname,
    ImportAsset,
    IPv4Address,
    IPv6Address,
    NetworkInterface,
    Software,
    Tag,
    ValidationError,
    Vulnerability,
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
    valid_attributes = {"valid-test": CustomAttribute("f" * 1024)}  # this tests backwards compat
    with pytest.raises(ValidationError):
        # CustomAttributes should already enforce a max length of 1024
        CustomAttribute("f" * 1025)

    valid_attributes2 = {"invalid-test": "f" * 1024}

    # However - it's still possible for a user to utilize a raw Dict[str, str] in its place
    invalid_attributes = {"invalid-test": "f" * 1025}

    # backwards compat test
    asset = ImportAsset(id="valid", custom_attributes=valid_attributes)
    assert len(asset.custom_attributes) == 1

    # current behavior test
    asset = ImportAsset(id="valid2", custom_attributes=valid_attributes2)
    assert len(asset.custom_attributes) == 1

    with pytest.raises(ValidationError):
        # thus, the ImportAsset itself should enforce this
        ImportAsset(id="invalid", custom_attributes=invalid_attributes)


def test_vuln_custom_attrs_length_limit():
    """
    This test ensures that `custom_attributes` for vulns has a length limit of 1024
    """
    valid_attributes = {f"foo-{n}": f"{n}" for n in range(1024)}
    invalid_attributes = {f"foo-{n}": f"{n}" for n in range(1025)}

    vuln = Vulnerability(id="foo", custom_attributes=valid_attributes)
    assert len(vuln.custom_attributes) == 1024

    with pytest.raises(ValidationError):
        Vulnerability(id="invalid", custom_attributes=invalid_attributes)


def test_vuln_attributes_key_length_limit():
    """
    This test ensures that the keys in the `custom_attributes` have a length limit of 256
    """
    valid_attributes = {"f" * 256: "valid-test"}
    invalid_attributes = {"f" * 257: "invalid-test"}

    asset = Vulnerability(id="valid", custom_attributes=valid_attributes)
    assert len(asset.custom_attributes) == 1

    with pytest.raises(ValidationError):
        Vulnerability(id="invalid", custom_attributes=invalid_attributes)


def test_vuln_attributes_value_length_limit():
    """
    This test ensures that the values in the `custom_attributes` have a length limit of 1024
    """
    valid_attributes = {"invalid-test": "f" * 1024}

    invalid_attributes = {"invalid-test": "f" * 1025}

    asset = Vulnerability(id="valid", custom_attributes=valid_attributes)
    assert len(asset.custom_attributes) == 1

    with pytest.raises(ValidationError):
        Vulnerability(id="invalid", custom_attributes=invalid_attributes)


def test_vuln_backwards_compat():
    """
    This test ensures that vuln custom attributes accept the deprecated CustomAttribute type
    in case a user uses it by mistake.
    """
    attr = {"foo": CustomAttribute("bar")}
    vuln = Vulnerability(id="test", custom_attributes=attr)
    assert len(vuln.custom_attributes) == 1


def test_import_asset_vulns_length_limit():
    """
    This test ensures that only 1000 vulns can be associated with a given asset
    """

    valid_vulns = [Vulnerability(id=f"foo-{x}") for x in range(1000)]
    invalid_vulns = [Vulnerability(id=f"foo-{x}") for x in range(1001)]

    asset = ImportAsset(id="valid", vulnerabilities=valid_vulns)
    assert len(asset.vulnerabilities) == 1000

    with pytest.raises(ValidationError):
        ImportAsset(id="invalid", vulnerabilities=invalid_vulns)


def test_vuln_uppercase_cve():
    """
    This test ensures that we try to uppercase the string given to us by the user for the CVE.

    We really shouldn't punish them for giving 'cve-1999-00001' instead of 'CVE-1999-00001'.
    """

    uppercase_cve = "CVE-1999-00001"
    lowercase_cve = "cve-1999-00001"
    invalid_cve = "cve-invalid"

    # should be valid and the cve remains cased the same
    vuln1 = Vulnerability(id="uppercase", cve=uppercase_cve)
    assert vuln1.cve == uppercase_cve

    # should be valid but now the cve is uppercase
    vuln2 = Vulnerability(id="lowercase", cve=lowercase_cve)
    assert vuln2.cve == uppercase_cve

    with pytest.raises(ValidationError):
        Vulnerability(id="invalid", cve=invalid_cve)


def test_vuln_lowercase_cpe():
    """
    This test ensures that we lowercase a CPE23 string for the user so that they don't get punished for regex.

    'CPE:2.3:*' should become 'cpe:2.3:*'.
    """

    lowercase_cpe = "cpe:2.3:*"
    uppercase_cpe = "CPE:2.3:*"
    invalid_cpe = "not-a-cpe:*"

    vuln1 = Vulnerability(id="lowercase", cpe23=lowercase_cpe)
    assert vuln1.cpe23 == lowercase_cpe

    vuln2 = Vulnerability(id="uppercase", cpe23=uppercase_cpe)
    assert vuln2.cpe23 == lowercase_cpe

    with pytest.raises(ValidationError):
        Vulnerability(id="invalid", cpe23=invalid_cpe)


def test_vuln_service_transport():
    """
    This test just ensures that a convenience wrapper works to lowercase the service transport string
    """

    upper = "TCP"
    lower = "tcp"

    vuln1 = Vulnerability(id="upper", service_transport=upper)
    assert vuln1.service_transport == lower

    vuln2 = Vulnerability(id="lower", service_transport=lower)
    assert vuln2.service_transport == lower


def test_vuln_service_address():
    """
    This test ensures a user can pass in valid strings to service_address
    """
    valid_ipv4 = IPv4Address("127.0.0.1")
    valid_ipv4_str = "1.1.1.1"
    valid_ipv6 = IPv6Address("2002:db7::")
    valid_ipv6_str = "2607:f8b0:4006:821::200e"
    invalid = "not-an-address"

    vuln = Vulnerability(id="ipv4", service_address=valid_ipv4)
    assert isinstance(vuln.service_address, IPv4Address)

    vuln = Vulnerability(id="ipv4_str", service_address=valid_ipv4_str)
    assert isinstance(vuln.service_address, IPv4Address)

    vuln = Vulnerability(id="ipv6", service_address=valid_ipv6)
    assert isinstance(vuln.service_address, IPv6Address)

    vuln = Vulnerability(id="ipv6_str", service_address=valid_ipv6_str)
    assert isinstance(vuln.service_address, IPv6Address)

    with pytest.raises(ValidationError):
        Vulnerability(id="invalid", service_address=invalid)


def test_software_custom_attrs_length_limit():
    """
    This test ensures that `custom_attributes` for software has a length limit of 1024
    """
    valid_attributes = {f"foo-{n}": f"{n}" for n in range(1024)}
    invalid_attributes = {f"foo-{n}": f"{n}" for n in range(1025)}

    sw = Software(id="foo", custom_attributes=valid_attributes)
    assert len(sw.custom_attributes) == 1024

    with pytest.raises(ValidationError):
        Software(id="invalid", custom_attributes=invalid_attributes)


def test_software_attributes_key_length_limit():
    """
    This test ensures that the keys in the `custom_attributes` have a length limit of 256
    """
    valid_attributes = {"f" * 256: "valid-test"}
    invalid_attributes = {"f" * 257: "invalid-test"}

    sw = Software(id="valid", custom_attributes=valid_attributes)
    assert len(sw.custom_attributes) == 1

    with pytest.raises(ValidationError):
        Software(id="invalid", custom_attributes=invalid_attributes)


def test_software_attributes_value_length_limit():
    """
    This test ensures that the values in the `custom_attributes` have a length limit of 1024
    """
    valid_attributes = {"invalid-test": "f" * 1024}

    invalid_attributes = {"invalid-test": "f" * 1025}

    sw = Software(id="valid", custom_attributes=valid_attributes)
    assert len(sw.custom_attributes) == 1

    with pytest.raises(ValidationError):
        Software(id="invalid", custom_attributes=invalid_attributes)


def test_software_service_address():
    """
    This test ensures a user can pass in valid strings to service_address
    """
    valid_ipv4 = IPv4Address("127.0.0.1")
    valid_ipv4_str = "1.1.1.1"
    valid_ipv6 = IPv6Address("2002:db7::")
    valid_ipv6_str = "2607:f8b0:4006:821::200e"
    invalid = "not-an-address"

    sw = Software(id="ipv4", service_address=valid_ipv4)
    assert isinstance(sw.service_address, IPv4Address)

    sw = Software(id="ipv4_str", service_address=valid_ipv4_str)
    assert isinstance(sw.service_address, IPv4Address)

    sw = Software(id="ipv6", service_address=valid_ipv6)
    assert isinstance(sw.service_address, IPv6Address)

    sw = Software(id="ipv6_str", service_address=valid_ipv6_str)
    assert isinstance(sw.service_address, IPv6Address)

    with pytest.raises(ValidationError):
        Software(id="invalid", service_address=invalid)


def test_software_backwards_compat():
    """
    This test ensures that vuln custom attributes accept the deprecated CustomAttribute type
    in case a user uses it by mistake.
    """
    attr = {"foo": CustomAttribute("bar")}
    sw = Software(id="test", custom_attributes=attr)
    assert len(sw.custom_attributes) == 1


def test_import_asset_software_length_limit():
    """
    This test ensures that only 1000 software can be associated with a given asset
    """

    valid_sw = [Software(id=f"foo-{x}") for x in range(1000)]
    invalid_sw = [Software(id=f"foo-{x}") for x in range(1001)]

    asset = ImportAsset(id="valid", software=valid_sw)
    assert len(asset.software) == 1000

    with pytest.raises(ValidationError):
        ImportAsset(id="invalid", software=invalid_sw)


def test_software_lowercase_cpe():
    """
    This test ensures that we lowercase a CPE23 string for the user so that they don't get punished for regex.

    'CPE:2.3:*' should become 'cpe:2.3:*'.
    """

    lowercase_cpe = "cpe:/a:2.3:*"
    uppercase_cpe = "CPE:/a:2.3:*"
    invalid_cpe = "not-a-cpe:*"

    sw1 = Software(id="lowercase", cpe23=lowercase_cpe)
    assert sw1.cpe23 == lowercase_cpe

    sw2 = Software(id="uppercase", cpe23=uppercase_cpe)
    assert sw2.cpe23 == lowercase_cpe

    with pytest.raises(ValidationError):
        Software(id="invalid", cpe23=invalid_cpe)


def test_software_service_transport():
    """
    This test just ensures that a convenience wrapper works to lowercase the service transport string
    """

    upper = "TCP"
    lower = "tcp"

    sw1 = Software(id="upper", service_transport=upper)
    assert sw1.service_transport == lower

    sw2 = Software(id="lower", service_transport=lower)
    assert sw2.service_transport == lower


def test_import_asset_hostnames():
    """
    This test ensures users can provide a string in place of a Hostname class for the hostnames field
    """
    valid = Hostname("test.com")
    valid_string = "test.io"
    invalid_string = "t" * 260 + ".com"  # 264 characters exceeds 260 char limit

    asset = ImportAsset(id="hostname", hostnames=[valid])
    assert len(asset.hostnames) == 1

    asset = ImportAsset(id="string", hostnames=[valid_string])
    assert len(asset.hostnames) == 1

    asset = ImportAsset(id="combined", hostnames=[valid, valid_string])
    assert len(asset.hostnames) == 2

    with pytest.raises(ValidationError):
        ImportAsset(id="includes_invalid_string", hostnames=[valid, valid_string, invalid_string])


def test_import_asset_tags():
    """
    This test ensures users can provide a string in place of a Tag class for the tags field
    """
    valid = Tag("test")
    valid_str = "also=test"
    invalid_str = "f" * 1025  # 1025 characters exceeds 1024 char limit

    asset = ImportAsset(id="tag", tags=[valid])
    assert len(asset.tags) == 1

    asset = ImportAsset(id="string", tags=[valid_str])
    assert len(asset.tags) == 1

    asset = ImportAsset(id="combined", tags=[valid, valid_str])
    assert len(asset.tags) == 2

    with pytest.raises(ValidationError):
        ImportAsset(id="includes_invalid_string", tags=[valid, valid_str, invalid_str])


def test_network_interfaces_ipv4():
    """
    This test ensures that a user can pass in strings for ipv4 addresses
    """
    valid = IPv4Address("127.0.0.1")
    valid_str = "1.1.1.1"
    invalid_str = "2002:db7::"  # this is an ipv6

    ni = NetworkInterface(ipv4_addresses=[valid])
    assert len(ni.ipv4_addresses) == 1

    ni = NetworkInterface(ipv4_addresses=[valid_str])
    assert len(ni.ipv4_addresses) == 1

    ni = NetworkInterface(ipv4_addresses=[valid, valid_str])
    assert len(ni.ipv4_addresses) == 2

    with pytest.raises(ValidationError):
        NetworkInterface(ipv4_addresses=[valid, valid_str, invalid_str])


def test_network_interfaces_ipv6():
    """
    This test ensures that a user can pass in strings for ipv6 addresses
    """
    valid = IPv6Address("2002:db7::")
    valid_str = "2607:f8b0:4006:821::200e"
    invalid_str = "1.1.1.1"  # this is an ipv6

    ni = NetworkInterface(ipv6_addresses=[valid])
    assert len(ni.ipv6_addresses) == 1

    ni = NetworkInterface(ipv6_addresses=[valid_str])
    assert len(ni.ipv6_addresses) == 1

    ni = NetworkInterface(ipv6_addresses=[valid, valid_str])
    assert len(ni.ipv6_addresses) == 2

    with pytest.raises(ValidationError):
        NetworkInterface(ipv6_addresses=[valid, valid_str, invalid_str])
