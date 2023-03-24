import pytest

from runzero import Error, assets_from_csv, assets_from_json
from runzero.types import ValidationError

from .utils import build_test_data_path


def test_assets_from_json_minimal_singular():
    data = '{"id": "foo123"}'
    asset = assets_from_json(data)
    assert len(asset) == 1
    assert asset[0].id == "foo123"


def test_assets_from_json_minimal_list():
    data = '[{"id": "foo123"}]'
    asset = assets_from_json(data)
    assert len(asset) == 1
    assert asset[0].id == "foo123"


@pytest.mark.parametrize(
    "data",
    [
        "malformed json",
        '{"missing": "id param", "which": "is required"}',
        "{'this': 'is', 'invalid': 'json', 'because': 'json', 'requires': 'double quotes'}",
    ],
)
def test_assets_from_json_invalid_json(data):
    with pytest.raises(ValidationError):
        assets_from_json(data)


def test_assets_from_json_additional_fields():
    data = '{"id": "foo123", "other_attribute": "foo"}'
    asset = assets_from_json(data)
    assert len(asset) == 1
    assert asset[0].id == "foo123"
    # TODO: the __root__ stuff is really unergonomic
    assert asset[0].custom_attributes["otherAttribute"].__root__ == "foo"


def test_assets_from_json_complex():
    data = """{"id": "foo123", \
"network_interfaces": [{"ipv4_addresses": ["192.0.2.1", "192.0.2.2"], \
"ipv6_addresses": ["2001:db8::", "2001:db7::"], "mac_address": "01:23:45:67:89:0A"}, \
{"ipv4_addresses": ["193.0.2.1"], \
"ipv6_addresses": ["2002:db7::"]}], \
"hostnames": ["host.domain.com", "host2.domain.com"], \
"domain": "domain.com", \
"first_seen_ts": "2023-03-06T18:14:50.52Z", \
"last_seen_ts": "2023-03-06T18:14:50.52Z", \
"os": "Ubuntu Linux 22.04", \
"os_version": "22.04", \
"manufacturer": "Apple Inc.", \
"model": "Macbook Air", \
"tags": ["foo", "key=value"], \
"device_type": "Desktop", \
"other_attribute": "foo", \
"another_attribute": "bar", \
"yet_another_attr": "baz"}"""
    assets = assets_from_json(data)
    assert len(assets) == 1

    asset = assets[0]
    assert asset.id == "foo123"
    assert len(asset.network_interfaces) == 2
    assert len(asset.network_interfaces[0].ipv4_addresses) == 2
    assert len(asset.network_interfaces[0].ipv6_addresses) == 2
    assert asset.network_interfaces[0].mac_address == "01:23:45:67:89:0A"
    assert len(asset.network_interfaces[1].ipv4_addresses) == 1
    assert len(asset.network_interfaces[1].ipv6_addresses) == 1
    assert asset.network_interfaces[1].mac_address is None
    assert len(asset.hostnames) == 2
    assert asset.domain == "domain.com"
    assert asset.first_seen_ts.isoformat() == "2023-03-06T18:14:50.520000+00:00"
    assert asset.last_seen_ts.isoformat() == "2023-03-06T18:14:50.520000+00:00"
    assert asset.os == "Ubuntu Linux 22.04"
    assert asset.os_version == "22.04"
    assert asset.manufacturer == "Apple Inc."
    assert asset.model == "Macbook Air"
    assert len(asset.tags) == 2
    assert asset.tags[0].__root__ == "foo"
    assert asset.tags[1].__root__ == "key=value"
    assert asset.device_type == "Desktop"
    assert len(asset.custom_attributes) == 3
    assert asset.custom_attributes["otherAttribute"].__root__ == "foo"
    assert asset.custom_attributes["anotherAttribute"].__root__ == "bar"
    assert asset.custom_attributes["yetAnotherAttr"].__root__ == "baz"


def test_assets_from_json_with_mapping():
    data = """{"custom_id": "foo123", \
"custom_hostnames": ["host.domain.com", "host2.domain.com"], \
"custom_domain": "domain.com", \
"other": "foo", \
"another_attribute": "bar"}"""

    mapping = {"id": "custom_id", "hostnames": "custom_hostnames", "domain": "custom_domain"}

    assets = assets_from_json(data, mapper=mapping)
    assert len(assets) == 1
    assert assets[0].id == "foo123"
    assert len(assets[0].hostnames) == 2
    assert assets[0].domain == "domain.com"
    assert len(assets[0].custom_attributes) == 2


def test_assets_from_json_multiple_with_mapping():
    data = """[{"custom_id": "foo123", \
"custom_hostnames": ["host.domain.com", "host2.domain.com"], \
"custom_domain": "domain.com"}, \
{"custom_id": "bar123", "other": "foo"}, \
{"id": "baz123"}]"""

    mapping = {"id": "custom_id", "hostnames": "custom_hostnames", "domain": "custom_domain"}

    assets = assets_from_json(data, mapper=mapping)
    assert len(assets) == 3
    assert assets[0].id == "foo123"
    assert len(assets[0].hostnames) == 2
    assert assets[0].domain == "domain.com"
    assert len(assets[0].custom_attributes) == 0
    assert assets[1].id == "bar123"
    assert assets[1].hostnames is None
    assert assets[1].domain is None
    assert len(assets[1].custom_attributes) == 1
    assert assets[2].id == "baz123"


@pytest.mark.parametrize("mapping", [None, [1, 2, 3]])
def test_assets_from_json_bad_mapping(mapping):
    data = '{"id": "foo123", "other_attribute": "foo"}'
    assets = assets_from_json(data, mapper=mapping)

    assert len(assets) == 1
    assert assets[0].id == "foo123"


def test_assets_from_csv_single_asset():
    file_path = build_test_data_path("single_asset.csv")
    assert file_path.exists()
    assets = assets_from_csv(file_path)
    assert len(assets) == 1
    assert assets[0].id == "foo123"
    assert assets[0].domain == "domain.com"
    assert len(assets[0].custom_attributes) == 3


@pytest.mark.parametrize(
    "file_path", [build_test_data_path("assets.csv"), build_test_data_path("assets.csv").as_posix()]
)
def test_assets_from_csv(file_path):
    assets = assets_from_csv(file_path)
    assert len(assets) == 3
    assert assets[0].id == "foo123"
    assert assets[0].domain == "domain.com"
    assert len(assets[0].custom_attributes) == 3
    assert assets[1].id == "bar1234"
    assert assets[1].domain == "domain2.com"
    assert len(assets[1].custom_attributes) == 3
    assert assets[2].id == "baz123"
    assert assets[2].domain == "domain3.com"
    assert len(assets[2].custom_attributes) == 3


def test_assets_from_csv_invalid_csv():
    file_path = build_test_data_path("bad.csv")
    assert file_path.exists()
    with pytest.raises(ValidationError):
        assets_from_csv(file_path)


def test_assets_from_csv_no_file():
    file_path = build_test_data_path("missing.csv")
    assert not file_path.exists()
    with pytest.raises(Error):
        assets_from_csv(file_path)


def test_assets_from_csv_with_field_mapping():
    file_path = build_test_data_path("rename_assets.csv")
    assert file_path.exists()

    mapping = {"id": "custom_id", "hostnames": "not_present_in_file", "domain": "custom_domain"}

    assets = assets_from_csv(file_path, mapper=mapping)
    assert len(assets) == 1
    assert assets[0].id == "foo123"
    assert assets[0].domain == "domain.com"
    assert assets[0].hostnames is None
    assert assets[0].device_type == "Desktop"
    assert len(assets[0].custom_attributes) == 1


@pytest.mark.parametrize("mapping", [None, [1, 2, 3]])
def test_assets_from_csv_with_bad_mapping(mapping):
    file_path = build_test_data_path("single_asset.csv")
    assert file_path.exists()

    assets = assets_from_csv(file_path, mapper=mapping)
    assert len(assets) == 1
    assert assets[0].id == "foo123"
