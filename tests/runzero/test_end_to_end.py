import time
from datetime import datetime, timezone

import pytest

from runzero.api import CustomAssets, CustomSourcesAdmin, OrgsAdmin, Sites, Tasks
from runzero.client import ClientError
from runzero.types import (
    CustomAttribute,
    Hostname,
    ImportAsset,
    IPv4Address,
    IPv6Address,
    NetworkInterface,
    OrgOptions,
    SiteOptions,
    Tag,
)


def build_test_data():
    return [
        ImportAsset(
            id="foo123",
            networkInterfaces=[
                NetworkInterface(
                    macAddress="01:23:45:67:89:0A",
                    ipv4Addresses=[IPv4Address("192.0.2.1"), IPv4Address("192.0.2.2")],
                    ipv6Addresses=[IPv6Address("2002:db7::")],
                )
            ],
            hostnames=[Hostname("host.domain.com"), Hostname("host2.domain.com")],
            domain="domain.com",
            firstSeenTS=datetime(2023, 3, 6, 18, 14, 50, 520000, tzinfo=timezone.utc),
            lastSeenTS=datetime(2023, 3, 6, 18, 14, 50, 520000, tzinfo=timezone.utc),
            os="Ubuntu Linux 22.04",
            osVersion="22.04",
            manufacturer="Apple Inc.",
            model="Macbook Air",
            tags=[Tag("foo"), Tag("key=value")],
            deviceType="Desktop",
            customAttributes={
                "otherAttribute": CustomAttribute("foo"),
                "anotherAttribute": CustomAttribute("bar"),
                "yetAnotherAttr": CustomAttribute("baz"),
            },
        )
    ]


@pytest.mark.integration_test
def test_client_end_to_end_import(account_client, request, tsstring):
    c = account_client
    org_name = tsstring(f"org for {request.node.name}")
    org_opts = OrgOptions(name=str(org_name))
    created_org = OrgsAdmin(client=c).create(org_opts)
    assert created_org.name == org_name

    site_name = tsstring(f"site for {request.node.name}")
    site_opts = SiteOptions(name=str(site_name))
    created_site = Sites(client=c).create(created_org.id, site_opts)
    assert created_site.name == site_name

    source_name = tsstring(f"source-for-{request.node.name}")
    custom_source = CustomSourcesAdmin(client=c).create(str(source_name))
    assert custom_source.name == source_name

    assets = build_test_data()

    created_task = CustomAssets(client=c).upload_assets(created_org.id, created_site.id, custom_source.id, assets)

    status = created_task.status
    iters = 0
    # keep polling until the task is completed or failed
    # timeout after 300 seconds
    while status not in ("processed", "failed", "error") and iters < 50:
        time.sleep(6)
        iters += 1
        status = Tasks(client=c).get_status(created_org.id, created_task.id)

    assert iters != 50  # this is a timeout issue
    assert status == "processed"

    # teardown Org
    OrgsAdmin(client=c).delete(created_org.id)
    with pytest.raises(ClientError):
        OrgsAdmin(client=c).get(created_org.id)

    # teardown custom source
    CustomSourcesAdmin(client=c).delete(custom_source.id)
    with pytest.raises(ClientError):
        CustomSourcesAdmin(client=c).get(source_id=custom_source.id)
