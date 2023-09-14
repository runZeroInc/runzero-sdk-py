import time
from datetime import datetime, timezone
from typing import List

import pytest

from runzero.api import CustomAssets, CustomIntegrationsAdmin, OrgsAdmin, Sites, Tasks
from runzero.client import ClientError
from runzero.types import (
    CustomAttribute,
    Hostname,
    ImportAsset,
    ImportTask,
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
            network_interfaces=[
                NetworkInterface(
                    mac_address="01:23:45:67:89:0A",
                    ipv4_addresses=[IPv4Address("192.0.2.1"), IPv4Address("192.0.2.2")],
                    ipv6_addresses=[IPv6Address("2002:db7::")],
                )
            ],
            hostnames=[Hostname("host.domain.com"), Hostname("host2.domain.com")],
            domain="domain.com",
            first_seen_ts=datetime(2023, 3, 6, 18, 14, 50, 520000, tzinfo=timezone.utc),
            os="Ubuntu Linux 22.04",
            os_version="22.04",
            manufacturer="Apple Inc.",
            model="Macbook Air",
            tags=[Tag("foo"), Tag("key=value")],
            device_type="Desktop",
            custom_attributes={
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
    custom_integration = CustomIntegrationsAdmin(client=c).create(str(source_name))
    assert custom_integration.name == source_name

    assets = build_test_data()

    created_task = CustomAssets(client=c).upload_assets(created_org.id, created_site.id, custom_integration.id, assets)

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

    # check the task stats to ensure correct processing
    task_info = Tasks(client=c).get(created_org.id, task_id=created_task.id)
    assert task_info is not None
    new_assets = task_info.stats.get("change.newAssets")
    assert new_assets is not None
    assert int(new_assets) == 1
    changed_assets = task_info.stats.get("change.changedAssets")
    assert changed_assets is not None
    assert int(changed_assets) == 0
    total_assets = task_info.stats.get("change.totalAssets")
    assert total_assets is not None
    assert int(total_assets) == 1

    # teardown Org
    OrgsAdmin(client=c).delete(created_org.id)
    with pytest.raises(ClientError):
        OrgsAdmin(client=c).get(created_org.id)

    # teardown custom integration
    CustomIntegrationsAdmin(client=c).delete(custom_integration.id)
    with pytest.raises(ClientError):
        CustomIntegrationsAdmin(client=c).get(custom_integration_id=custom_integration.id)


def build_assets() -> List[ImportAsset]:
    return [
        ImportAsset(
            id="test1",
            network_interfaces=[
                NetworkInterface(
                    mac_address="01:23:45:67:89:0A",
                    ipv4_addresses=[IPv4Address("192.0.2.1")],
                    ipv6_addresses=[IPv6Address("2002:db7::")],
                )
            ],
            hostnames=[Hostname("host.domain.com")],
            domain="domain.com",
            first_seen_ts=datetime(2023, 3, 6, 18, 14, 50, 520000, tzinfo=timezone.utc),
            os="Ubuntu Linux 22.04",
            os_version="22.04",
            manufacturer="Apple Inc.",
            model="Macbook Air",
            tags=[Tag("foo"), Tag("key=value")],
            device_type="Desktop",
            custom_attributes={
                "otherAttribute": CustomAttribute("foo1"),
            },
        ),
        # Has different id, mac/ipv4, first seen ts, and custom attributes
        ImportAsset(
            id="test2",
            network_interfaces=[
                NetworkInterface(
                    mac_address="01:32:54:67:89:0A",
                    ipv4_addresses=[IPv4Address("192.2.1.1")],
                )
            ],
            hostnames=[Hostname("host.domain.com")],
            domain="domain.com",
            first_seen_ts=datetime(2023, 4, 1, 18, 14, 50, 520000, tzinfo=timezone.utc),
            os="Ubuntu Linux 22.04",
            os_version="22.04",
            manufacturer="Apple Inc.",
            model="Macbook Air",
            tags=[Tag("foo"), Tag("key=value")],
            device_type="Desktop",
            custom_attributes={
                "otherAttribute": CustomAttribute("foo2"),
            },
        ),
        # Has different id, mac/ipv4, first seen ts, and custom attributes
        ImportAsset(
            id="test3",
            network_interfaces=[
                NetworkInterface(
                    mac_address="01:32:45:76:98:0B",
                    ipv4_addresses=[IPv4Address("192.4.2.3")],
                )
            ],
            hostnames=[Hostname("host.domain.com")],
            domain="domain.com",
            first_seen_ts=datetime(2023, 1, 1, 18, 14, 50, 520000, tzinfo=timezone.utc),
            os="Ubuntu Linux 22.04",
            os_version="22.04",
            manufacturer="Apple Inc.",
            model="Macbook Air",
            tags=[Tag("foo"), Tag("key=value")],
            device_type="Desktop",
            custom_attributes={
                "otherAttribute": CustomAttribute("foo3"),
            },
        ),
    ]


@pytest.mark.integration_test
def test_asset_import_exclude_unknown(account_client, temp_org, temp_custom_integration):
    """
    This test utilizes a temp org/site/integration to ensure idempotency

    1. uploads a single asset with "exclude unknown" set to false
    2. asserts that 1 asset was created by checking the task stats after completion
    3. uploads 3 assets (2 new - and 1 which will merge to the previously uploaded) with "exclude unknown" set to true
    4. asserts that 1 asset was updated and no new assets were created
    5. re-uploads the previous 3 assets (2 new - and 1 which will merge to the previously uploaded) with "exclude
        unknown" set to false
    6. asserts that 1 asset was updated and 2 assets were created by checking the task stats after completion
    """
    c = account_client
    # create the 3 assets we will use through this test
    assets = build_assets()

    # create our temp site
    site = Sites(client=c).create(temp_org.id, site_options=SiteOptions(name="temp-site-for-exclude-unknown-test"))

    # upload our first asset
    first_asset = [assets[0]]
    first_created_task = CustomAssets(client=c).upload_assets(
        temp_org.id,
        site.id,
        temp_custom_integration.id,
        first_asset,
        task_info=ImportTask(name="first", exclude_unknown=False),
    )

    # check that the task successfully completed
    status = first_created_task.status
    iters = 0
    # keep polling until the task is completed or failed
    # timeout after 300 seconds
    while status not in ("processed", "failed", "error") and iters < 50:
        time.sleep(6)
        iters += 1
        status = Tasks(client=c).get_status(temp_org.id, first_created_task.id)
    assert iters != 50  # this is a timeout issue
    assert status == "processed"

    # check out the stats of the first task
    # should be:
    # - 1 new asset
    # - 0 changed assets
    # - 0 ignored assets (skipped for now)
    # - 1 asset total
    first_created_task = Tasks(client=c).get(temp_org.id, task_id=first_created_task.id)
    assert first_created_task is not None
    new_assets = first_created_task.stats.get("change.newAssets")
    assert new_assets is not None
    assert int(new_assets) == 1
    changed_assets = first_created_task.stats.get("change.changedAssets")
    assert changed_assets is not None
    assert int(changed_assets) == 0
    # skipping ignored assets as this feature is currently broken
    # ignored_assets = first_created_task.stats.get("change.ignoredAssets")
    # assert ignored_assets is not None
    # assert int(ignored_assets) == 0
    total_assets = first_created_task.stats.get("change.totalAssets")
    assert total_assets is not None
    assert int(total_assets) == 1

    # upload our next set of assets
    second_assets = assets
    # modifying the first asset to make sure we get an update on merge
    second_assets[0].device_type = "Laptop"
    second_created_task = CustomAssets(client=c).upload_assets(
        temp_org.id,
        site.id,
        temp_custom_integration.id,
        second_assets,
        task_info=ImportTask(name="second", exclude_unknown=True),
    )

    # check that the task successfully completed
    status = second_created_task.status
    iters = 0
    # keep polling until the task is completed or failed
    # timeout after 300 seconds
    while status not in ("processed", "failed", "error") and iters < 50:
        time.sleep(6)
        iters += 1
        status = Tasks(client=c).get_status(temp_org.id, second_created_task.id)
    assert iters != 50  # this is a timeout issue
    assert status == "processed"

    # check out the stats of the second task
    # should be:
    # - 0 new asset
    # - 1 changed assets
    # - 2 ignored assets (skipped for now)
    # - 1 asset total
    second_created_task = Tasks(client=c).get(temp_org.id, task_id=second_created_task.id)
    assert second_created_task is not None
    new_assets = second_created_task.stats.get("change.newAssets")
    assert new_assets is not None
    assert int(new_assets) == 0
    changed_assets = second_created_task.stats.get("change.changedAssets")
    assert changed_assets is not None
    assert int(changed_assets) == 1
    # skipping ignored assets as this feature is currently broken
    # ignored_assets = second_created_task.stats.get("change.ignoredAssets")
    # assert ignored_assets is not None
    # assert int(ignored_assets) == 2
    total_assets = second_created_task.stats.get("change.totalAssets")
    assert total_assets is not None
    assert int(total_assets) == 1

    # upload our final set of assets
    third_assets = assets
    # modifying the first asset again to make sure we get an update on merge
    third_assets[0].device_type = "Server"
    third_created_task = CustomAssets(client=c).upload_assets(
        temp_org.id,
        site.id,
        temp_custom_integration.id,
        third_assets,
        task_info=ImportTask(name="third", exclude_unknown=False),
    )

    # check that the task successfully completed
    status = third_created_task.status
    iters = 0
    # keep polling until the task is completed or failed
    # timeout after 300 seconds
    while status not in ("processed", "failed", "error") and iters < 50:
        time.sleep(6)
        iters += 1
        status = Tasks(client=c).get_status(temp_org.id, third_created_task.id)
    assert iters != 50  # this is a timeout issue
    assert status == "processed"

    # check out the stats of the third task
    # should be:
    # - 2 new asset
    # - 1 changed assets
    # - 0 should be ignored (skipped for now)
    # - 3 asset total
    third_created_task = Tasks(client=c).get(temp_org.id, task_id=third_created_task.id)
    assert third_created_task is not None
    new_assets = third_created_task.stats.get("change.newAssets")
    assert new_assets is not None
    assert int(new_assets) == 2
    changed_assets = third_created_task.stats.get("change.changedAssets")
    assert changed_assets is not None
    assert int(changed_assets) == 1
    # skipping ignored assets as this feature is currently broken
    # ignored_assets = third_created_task.stats.get("change.ignoredAssets")
    # assert ignored_assets is not None
    # assert int(ignored_assets) == 0
    total_assets = third_created_task.stats.get("change.totalAssets")
    assert total_assets is not None
    assert int(total_assets) == 3
