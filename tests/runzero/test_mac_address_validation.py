import pydantic
import pytest

from runzero.types import ImportAsset, NetworkInterface, ValidationError


@pytest.mark.parametrize(
    "mac",
    [
        pytest.param("01:23:45:67:89:AB", id="MAC/EUI-48 colons"),
        pytest.param("01-23-45-67-89-ab", id="MAC/EUI-48 dashes"),
        pytest.param("0123.4567.89ab", id="MAC/EUI-48 dotted quads"),
        pytest.param("01:23:45:67:89:ab:cd:ef", id="EUI-64 colons"),
        pytest.param("0123.4567.89ab.cdef", id="EUI-64 dotted quads"),
        pytest.param("01-23-45-67-89-ab-cd-ef", id="EUI-64 dashes"),
        pytest.param("0123 4567 89ab cdEF", id="EUI-64 spaces"),
    ],
)
def test_valid_mac_addresses(mac):
    ImportAsset(
        id="foo123", os="Debian", osVersion="123.456", networkInterfaces=[NetworkInterface(macAddress=str(mac))]
    )
    ImportAsset(
        id="foo123", os="Debian", osVersion="123.456", networkInterfaces=[NetworkInterface(macAddress=str(mac).upper())]
    )
    ImportAsset(
        id="foo123", os="Debian", osVersion="123.456", networkInterfaces=[NetworkInterface(macAddress=str(mac).lower())]
    )


@pytest.mark.parametrize(
    "badmac",
    [
        pytest.param("", id="blank"),
        pytest.param("junk", id="hex free, not a mac"),
        pytest.param("ajunkb", id="hex included, not a mac"),
        pytest.param("abcd", id="all hex, not a mac"),
        pytest.param("01:23:45:67:89:AB:CX", id="MAC/EUI-48 colons with bad hex char"),
        pytest.param("0123 4567 89ab cdEFAB", id="EUI-64 spaces, too long, no separator"),
        pytest.param("01:89:AB", id="MAC/EUI-48 colons, too short"),
        pytest.param("01:23:45:67:89:AB:CD", id="MAC/EUI-48 colons, too long, too short for 64"),
        pytest.param("01-23-45-67-89-ax", id="MAC/EUI-48 dashes with bad hex char"),
        pytest.param("01-23-45-67-89:ab", id="MAC/EUI-48 dashes with mixed sep"),
        pytest.param("01-23-45-67", id="MAC/EUI-48 dashes, too short"),
        pytest.param("01-23-45-67-89-ab-ba", id="MAC/EUI-48 dashes, too long, too short for 64"),
        pytest.param("0123.4567.89ax", id="MAC/EUI-48 dotted quads with bad hex char"),
        pytest.param("0123.4567-89ab", id="MAC/EUI-48 dotted quads with mixed sep"),
        pytest.param("0123.4567.89", id="MAC/EUI-48 dotted quads, too short"),
        pytest.param("0123.4567.89bc.cd", id="MAC/EUI-48 dotted quads, too long, too short for 64"),
        pytest.param("01:23:45:67:89:ab:cd:ex", id="EUI-64 colons with bad hex char"),
        pytest.param("01:23:45:67:89:ab:cd-ea", id="EUI-64 colons with mixed sep"),
        pytest.param("01:23:45:67:89:ab:cd", id="EUI-64 colons, too short"),
        pytest.param("01:23:45:67:89:ab:cd:ef:ab", id="EUI-64 colons, too long"),
        pytest.param("0123.4567.89ab.cdex", id="EUI-64 dotted quads with bad hex char"),
        pytest.param("0123.4567.89ab-cdef", id="EUI-64 dotted quads with mixed sep"),
        pytest.param("0123.4567.89ab.cd", id="EUI-64 dotted quads, too short"),
        pytest.param("0123.4567.89ab.cdef.ab", id="EUI-64 dotted quads, too long"),
        pytest.param("01-23-45-67-89-ab-cd-ex", id="EUI-64 dashes with bad hex char"),
        pytest.param("01-23-45-67-89-ab-cd:ef", id="EUI-64 dashes with mixed sep"),
        pytest.param("01-23-45-67-89-ab-cd", id="EUI-64 dashes, too short"),
        pytest.param("01-23-45-67-89-ab-cd-ef-ab", id="EUI-64 dashes, too long"),
        pytest.param("0123 4567 89ab cdEX", id="EUI-64 spaces with bad hex char"),
        pytest.param("0123 4567 89ab-cdEF", id="EUI-64 spaces with mixed sep"),
        pytest.param("0123 4567 89ab cd", id="EUI-64 spaces, too short"),
        pytest.param("0123 4567 89ab cdEF AB", id="EUI-64 spaces, too long"),
        pytest.param("0123 4567 89ab cdEFAB", id="EUI-64 spaces, too long, no separator"),
    ],
)
def test_invalid_mac_addresses(badmac):
    with pytest.raises(pydantic.ValidationError):
        ImportAsset(
            id="foo123", os="Debian", osVersion="123.456", networkInterfaces=[NetworkInterface(macAddress=str(badmac))]
        )
        ImportAsset(
            id="foo123",
            os="Debian",
            osVersion="123.456",
            networkInterfaces=[NetworkInterface(macAddress=str(badmac).upper())],
        )
        ImportAsset(
            id="foo123",
            os="Debian",
            osVersion="123.456",
            networkInterfaces=[NetworkInterface(macAddress=str(badmac).lower())],
        )
