import json
from ipaddress import ip_address
from typing import Any, Dict, List
from uuid import UUID

from runzero.types import (
    CustomAttribute,
    ImportAsset,
    IPv4Address,
    IPv6Address,
    NetworkInterface,
)


def build_assets_from_json(
    json_input: List[Dict[str, Any]], asset_id_force_merge_lookup: Dict[str, UUID]
) -> List[ImportAsset]:
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

        # Consider the runZero ID for force-merging if you know it ahead of time. In this case, if the asset's ID and
        # the runZero ID mapped, runZero will force the merge rather than using the built-in merge logic which matches
        # using various ImportAsset fields.
        #
        # Assets can be bulk-exported from runZero and examined programmatically allowing for very custom,
        # arbitrarily-defined merge/match rules to be executed. Any program you can write to match an ImportAsset object
        # to a runZero asset ID is an encoding of merge/match rules you've defined for any data set or situation.
        runZero_id = asset_id_force_merge_lookup.get(asset_id, None)
        assets.append(
            ImportAsset(
                id=asset_id,
                domain=asset_domain,
                deviceType=asset_type,
                networkInterfaces=[network],
                customAttributes=custom_attrs,
                run_zero_id=runZero_id,  # If not None, will try to force the merge
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

    # This is asset data from another system. runZero doesn't need to know how that system represents
    # data. Instead, simple scripts like this can perform the translation from arbitrary data - in this case JSON data -
    # to the ImportAsset type.
    data_from_other_api = """\
[{"asset_id": "someId1", "asset_domain": "some.domain.com", "other_attribute": "small", "type": "Tablet",\
"mac": "6F:C2:BF:22:E8:38", "ip_addresses": ["101.82.74.140", "9.216.6.20"], "drive_type": "ssd"},\
{"asset_id": "someId2", "asset_domain": "other.domain.com", "other_attribute": "medium", "type": "Desktop",\
"mac": "1D:E6:64:DA:3D:87", "ip_addresses": ["140.0.21.251"], "drive_type": "hdd", "unexpected_attribute": "XL"},\
{"asset_id": "someId3", "asset_domain": "another.domain.com", "other_attribute": "large", "type": "Server",\
"mac": "A6:C5:E7:6A:85:4A", "ip_addresses": ["6946:e4fb:963b:9ab2:1943:b4d6:7d14:b041", "180.169.16.247"]}]\
"""

    # For one asset above, we know the runZero GUID and will force the merge of the external data
    # to the target runZero asset ID, bypassing merge logic rules based on other properties.
    asset_id_force_merge_lookup = {
        # This system's asset ID     :     runZero asset GUID
        "someId3": UUID("7e7febcc-924d-4a78-935b-bb35dad9c5ac")
    }

    assets = build_assets_from_json(json.loads(data_from_other_api), asset_id_force_merge_lookup)
    print(f"created {len(assets)} ImportAssets from our API data")

    # here we iterate over the assets and confirm that the values were parsed correctly
    for asset in assets:
        print(f"id: {asset.id}")
        print(f"domain: {asset.domain}")
        print(f"device type: {asset.device_type}")
        print(f"additional attributes: {asset.custom_attributes}")
        if asset.run_zero_id is not None:
            print(f"asset {asset.id} will be force-merged onto runZero asset ID {asset.run_zero_id}")

    # Now that these assets are each translated to an ImportAsset object, they can be bulk-uploaded
    # to runZero which will try to merge them onto existing assets. See:
    # examples/create_assets_from_json.py
    # for an example of how to upload our external asset data into runZero


if __name__ == "__main__":
    main()
