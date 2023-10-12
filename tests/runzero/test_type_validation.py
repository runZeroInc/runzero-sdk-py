import pytest

from runzero.types import (
    AddressValueError,
    CustomAttribute,
    ImportAsset,
    IPv4Address,
    IPv6Address,
    NetworkInterface,
    Software,
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
