import json
from ipaddress import ip_address
from typing import Any, Dict, List

from runzero.types import (
    CustomAttribute,
    ImportAsset,
    IPv4Address,
    IPv6Address,
    NetworkInterface,
)


def build_assets_from_json(json_input: List[Dict[str, Any]]) -> List[ImportAsset]:
    """
    This is an example function to highlight how to handle converting data from an API into the ImportAsset format that
    is required for uploading to the runZero platform.

    This function assumes that the json has been converted into a list of dictionaries using `json.loads()` (or any
    similar functions).
    """

    assets: List[ImportAsset] = []
    for item in json_input:
        # grab known API attributes from the json dict that are always present
        asset_id = item.pop("asset_id")
        asset_domain = item.pop("asset_domain")
        asset_type = item.pop("type")
        other_attr = item.pop("other_attribute")
        mac = item.pop("mac")
        ip = item.pop("ip_addresses")

        # create the network interface
        network = build_network_interface(mac, ip)

        # handle the custom attributes
        custom_attrs: Dict[str, CustomAttribute] = {"otherAttribute": CustomAttribute(other_attr)}
        # in this case drive might not always be present and needs to be checked
        drive = item.get("drive_type")
        if drive is not None:
            custom_attrs["driveType"] = CustomAttribute(item.pop("drive_type"))

        # handle any additional values and insert into custom_attrs
        # this works because of the use of items.pop for all other attributes which removed them from the dict
        for key, value in item.items():
            custom_attrs[key] = CustomAttribute(value)

        assets.append(
            ImportAsset(
                id=asset_id,
                domain=asset_domain,
                deviceType=asset_type,
                networkInterfaces=[network],
                customAttributes=custom_attrs,
            )
        )
    return assets


def build_network_interface(mac: str, ips: List[str]) -> NetworkInterface:
    """
    This function converts a mac and a list of strings in either ipv4 or ipv6 format and creates a NetworkInterface that
    is accepted in the ImportAsset
    """
    ip4s: List[IPv4Address] = []
    ip6s: List[IPv6Address] = []
    for ip in ips:
        ip_addr = ip_address(ip)
        if ip_addr.version == 4:
            ip4s.append(ip_addr)
        elif ip_addr.version == 6:
            ip6s.append(ip_addr)
        else:
            continue

    return NetworkInterface(macAddress=mac, ipv4Addresses=ip4s, ipv6Addresses=ip6s)


def main():
    """
    This SDK provides tooling to convert JSON from another external API, however there are some gotchas around mapping
    the fields from one source and getting it to conform to an ImportAsset.

    The below code provides a very simple example to convert JSON from one format into an ImportAsset
    """
    data_from_other_api = """\
[{"asset_id": "someId1", "asset_domain": "some.domain.com", "other_attribute": "small", "type": "Tablet",\
"mac": "6F:C2:BF:22:E8:38", "ip_addresses": ["101.82.74.140", "9.216.6.20"], "drive_type": "ssd"},\
{"asset_id": "someId2", "asset_domain": "other.domain.com", "other_attribute": "medium", "type": "Desktop",\
"mac": "1D:E6:64:DA:3D:87", "ip_addresses": ["140.0.21.251"], "drive_type": "hdd", "unexpected_attribute": "XL"},\
{"asset_id": "someId3", "asset_domain": "another.domain.com", "other_attribute": "large", "type": "Server",\
"mac": "A6:C5:E7:6A:85:4A", "ip_addresses": ["6946:e4fb:963b:9ab2:1943:b4d6:7d14:b041", "180.169.16.247"]}]\
"""

    assets = build_assets_from_json(json.loads(data_from_other_api))
    print(f"created {len(assets)} ImportAssets from our API data")

    # here we iterate over the assets and confirm that the values were parsed correctly
    for asset in assets:
        print(f"id: {asset.id}")
        print(f"domain: {asset.domain}")
        print(f"device type: {asset.device_type}")
        print(f"additional attributes: {asset.custom_attributes}")


if __name__ == "__main__":
    main()
