import time
from datetime import datetime, timezone
from typing import List

import pytest

from runzero.api import CustomAssets, CustomIntegrationsAdmin, OrgsAdmin, Sites, Tasks
from runzero.client import ClientError
from runzero.types import (
    Hostname,
    ImportAsset,
    ImportTask,
    IPv4Address,
    IPv6Address,
    NetworkInterface,
    OrgOptions,
    Service,
    ServiceProtocolData,
    SiteOptions,
    Software,
    Tag,
    Vulnerability,
)

__TIMEOUT = 100


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
                "otherAttribute": "foo",
                "anotherAttribute": "bar",
                "yetAnotherAttr": "baz",
            },
        )
    ]


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
                "otherAttribute": "foo1",
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
                "otherAttribute": "foo2",
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
                "otherAttribute": "foo3",
            },
        ),
    ]


def build_vulns() -> List[Vulnerability]:
    return [
        Vulnerability(
            id="vuln-1",
            category="openssl",
            name="my name",
            description="a terse description of the vuln",
            solution="try turning it off and back on again",
            service_address=IPv4Address("127.0.0.1"),
            service_transport="tcp",
            service_port=8080,
            cpe23="cpe:/o:google:*",
            cve="CVE-2022-31005",
            cvss2_base_score=4.3,
            cvss2_temporal_score=2.2,
            cvss3_base_score=5.1,
            cvss3_temporal_score=4.3,
            severity_rank=3,
            severity_score=6.6,
            risk_rank=4,
            risk_score=211.4,
            exploitable=True,
            published_ts=datetime(2023, 3, 6, 18, 14, 50, 520000, tzinfo=timezone.utc),
            first_detected_ts=datetime(2023, 3, 6, 18, 14, 50, 520000, tzinfo=timezone.utc),
            last_detected_ts=datetime(2023, 3, 6, 18, 14, 50, 520000, tzinfo=timezone.utc),
            custom_attributes={"foo": "bar"},
        ),
        Vulnerability(
            id="vuln-2",
            category="wifi",
            name="other name",
            description="bueler?",
            solution="just throw it out",
            service_address=IPv4Address("0.0.0.1"),
            service_transport="udp",
            service_port=10001,
            cpe23="cpe:/o:libwebp:*",
            cve="CVE-2021-11001",
            cvss2_base_score=2.1,
            cvss2_temporal_score=2.2,
            cvss3_base_score=5.1,
            cvss3_temporal_score=4.3,
            severity_rank=2,
            severity_score=3.6,
            risk_rank=1,
            risk_score=19.4,
            exploitable=True,
            published_ts=datetime(2023, 3, 6, 18, 14, 50, 520000, tzinfo=timezone.utc),
            first_detected_ts=datetime(2023, 3, 6, 18, 14, 50, 520000, tzinfo=timezone.utc),
            last_detected_ts=datetime(2023, 3, 6, 18, 14, 50, 520000, tzinfo=timezone.utc),
            custom_attributes={"foo": "bar"},
        ),
        Vulnerability(
            id="vuln-3",
            category="roomba",
            name="demon in my vacuum",
            description="dont trust vacuums",
            solution="there is no solution - the uprising is inevitable",
            service_address=IPv6Address("2002:db7::"),
            service_transport="grpc",
            service_port=443,
            cpe23="cpe:/*",
            cve="CVE-2045-11001",
            cvss2_base_score=2.1,
            cvss2_temporal_score=2.2,
            cvss3_base_score=5.1,
            cvss3_temporal_score=4.3,
            severity_rank=4,
            severity_score=3.6,
            risk_rank=4,
            risk_score=19.4,
            exploitable=False,
            published_ts=datetime(2023, 3, 6, 18, 14, 50, 520000, tzinfo=timezone.utc),
            first_detected_ts=datetime(2023, 3, 6, 18, 14, 50, 520000, tzinfo=timezone.utc),
            last_detected_ts=datetime(2023, 3, 6, 18, 14, 50, 520000, tzinfo=timezone.utc),
            custom_attributes={"foo": "bar"},
        ),
    ]


def build_software() -> List[Software]:
    return [
        Software(
            id="test-sw-1",
            service_address=IPv6Address("2002:db7::"),
            service_transport="grpc",
            service_port=443,
            cpe23="cpe:/a:/test/*",
            installed_at=datetime(2023, 3, 6, 18, 14, 50, 520000, tzinfo=timezone.utc),
            installed_from="apt-ubuntu-20.14-LTS",
            installed_size=1564857439,
            vendor="test-vendor",
            # product ensures multibyte char support. contains 129 bytes and 74 chars.
            # limit for field should be 128 chars and not 128 bytes.
            product="Плагин пользователя систем электронного правительства (версия 3.1.1.0) x64",
            version="v1.2.3.004a",
            update="service pack 2",
            language="russian",
            software_edition="ultimate",
            target_software="macOS",
            target_hardware="m2",
            other="test",
            custom_attributes={"foo": "bar"},
        )
    ]


def build_services() -> List[Service]:
    return [
        Service(
            address=IPv4Address("192.0.2.1"),
            port=443,
            transport="tcp",
            # intentionally excluding listing a vendor and version value
            product="Django",
            protocol_data=[
                ServiceProtocolData(name="https", attributes={"service-name": "my-python-server", "use-tls": "false"}),
                ServiceProtocolData(name="tls", attributes={"alive": "false"}),
                ServiceProtocolData(name="dns", attributes={"cloudflare-approved": "false", "is_legitimate": "false"}),
            ],
            custom_attributes={"foo": "bar", "test": "test-test"},
        ),
        Service(
            address=IPv4Address("192.0.7.1"),
            port=50051,
            transport="rpc",
            vendor="NATS",
            product="NATS Jetstream",
            version="3.4.2",
            protocol_data=[
                ServiceProtocolData(
                    name="grpc", attributes={"type": "unary", "supports_bidirectional_stream": "maybe"}
                ),
            ],
            custom_attributes={"test-1": "TEST_two"},
        ),
        Service(
            address=IPv4Address("192.0.7.2"),
            port=21,
            transport="tcp",
            protocol_data=[
                ServiceProtocolData(name="ftp", attributes={"secure": "no."}),
            ],
        ),
    ]


@pytest.mark.skip(reason="not updated for latest behavior")
@pytest.mark.integration_test
def test_client_end_to_end_import(account_client, request, tsstring):
    """
    This test does the following:

    1. Creates a new Org
    2. Creates a site in that Org
    3. Creates a custom integration source
    4. Creates an asset to upload
    5. Uploads the asset for processing
    6. Checks the status of the created task and expects it to successfully complete
    7. Checks the stats of the task to ensure it created the expected new asset
    8. Deletes the Site
    9. Checks that the site was in fact deleted
    10. Deletes the Org
    11. Checks that the org was in fact deleted
    12. Deletes the custom integration source
    13. Checks that the custom integration source was in fact deleted
    """
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
    while status not in ("processed", "failed", "error") and iters < __TIMEOUT:
        time.sleep(6)
        iters += 1
        status = Tasks(client=c).get_status(created_org.id, created_task.id)

    assert iters != __TIMEOUT  # this is a timeout issue
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

    # teardown site
    Sites(client=c).delete(created_org.id, created_site.id)
    with pytest.raises(ClientError):
        Sites(client=c).get(created_org.id, site_id=created_site.id)

    # teardown Org
    OrgsAdmin(client=c).delete(created_org.id)
    with pytest.raises(ClientError):
        OrgsAdmin(client=c).get(created_org.id)

    # teardown custom integration
    CustomIntegrationsAdmin(client=c).delete(custom_integration.id)
    with pytest.raises(ClientError):
        CustomIntegrationsAdmin(client=c).get(custom_integration_id=custom_integration.id)


@pytest.mark.skip(reason="not updated for latest behavior")
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
    while status not in ("processed", "failed", "error") and iters < __TIMEOUT:
        time.sleep(6)
        iters += 1
        status = Tasks(client=c).get_status(temp_org.id, first_created_task.id)
    assert iters != __TIMEOUT  # this is a timeout issue
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
    while status not in ("processed", "failed", "error") and iters < __TIMEOUT:
        time.sleep(6)
        iters += 1
        status = Tasks(client=c).get_status(temp_org.id, second_created_task.id)
    assert iters != __TIMEOUT  # this is a timeout issue
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
    while status not in ("processed", "failed", "error") and iters < __TIMEOUT:
        time.sleep(6)
        iters += 1
        status = Tasks(client=c).get_status(temp_org.id, third_created_task.id)
    assert iters != __TIMEOUT  # this is a timeout issue
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


@pytest.mark.integration_test
def test_client_custom_attr_len(account_client, temp_org, temp_custom_integration):
    """
    This test ensures we can upload an asset with up to 1024 custom attributes and have it process successfully.
    """
    c = account_client
    # create our test asset
    asset = build_test_data()
    # then add up to 1024 custom attributes to it
    asset[0].custom_attributes = {f"foo-{n}": f"{n}" for n in range(1024)}
    assert len(asset[0].custom_attributes) == 1024

    # create our temp site
    site = Sites(client=c).create(temp_org.id, site_options=SiteOptions(name="temp-site-for-exclude-unknown-test"))

    # upload our asset
    created_task = CustomAssets(client=c).upload_assets(
        temp_org.id,
        site.id,
        temp_custom_integration.id,
        asset,
        task_info=ImportTask(name="first", exclude_unknown=False),
    )

    status = created_task.status
    iters = 0
    # keep polling until the task is completed or failed
    # timeout after 300 seconds
    while status not in ("processed", "failed", "error") and iters < __TIMEOUT:
        time.sleep(6)
        iters += 1
        status = Tasks(client=c).get_status(temp_org.id, created_task.id)

    assert iters != __TIMEOUT  # this is a timeout issue
    assert status == "processed"

    # check the task stats to ensure correct processing
    task_info = Tasks(client=c).get(temp_org.id, task_id=created_task.id)
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


@pytest.mark.integration_test
def test_asset_import_include_vulns(account_client, temp_org, temp_custom_integration_with_icon):
    """
    This test utilizes a temp org/site/integration to ensure idempotency

    1. uploads a single asset with 3 vulnerabilities
    2. asserts that 1 asset was created by checking the task stats after completion successfully completes
    """
    c = account_client
    # create the 3 assets we will use through this test
    assets = build_test_data()
    # add our vuln data
    assets[0].vulnerabilities = build_vulns()

    # create our temp site
    site = Sites(client=c).create(temp_org.id, site_options=SiteOptions(name="temp-site-for-includes-vulns-test"))

    # upload our first asset
    vuln_task = CustomAssets(client=c).upload_assets(
        temp_org.id,
        site.id,
        temp_custom_integration_with_icon.id,
        assets,
        task_info=ImportTask(name="with-vulns", exclude_unknown=False),
    )

    # check that the task successfully completed
    status = vuln_task.status
    iters = 0
    # keep polling until the task is completed or failed
    # timeout after 300 seconds
    while status not in ("processed", "failed", "error") and iters < __TIMEOUT:
        time.sleep(6)
        iters += 1
        status = Tasks(client=c).get_status(temp_org.id, vuln_task.id)
    assert iters != __TIMEOUT  # this is a timeout issue
    assert status == "processed"

    # check out the stats of the first task
    # should be:
    # - 1 new asset
    # - 0 changed assets
    # - 1 asset total
    vuln_task = Tasks(client=c).get(temp_org.id, task_id=vuln_task.id)
    assert vuln_task is not None
    new_assets = vuln_task.stats.get("change.newAssets")
    assert new_assets is not None
    assert int(new_assets) == 1
    changed_assets = vuln_task.stats.get("change.changedAssets")
    assert changed_assets is not None
    assert int(changed_assets) == 0
    total_assets = vuln_task.stats.get("change.totalAssets")
    assert total_assets is not None
    assert int(total_assets) == 1


@pytest.mark.integration_test
def test_asset_import_include_software(account_client, temp_org, temp_custom_integration_with_icon):
    """
    This test utilizes a temp org/site/integration to ensure idempotency

    1. uploads a single asset with a piece of software associated with the asset
    2. asserts that 1 asset was created by checking the task stats after completion successfully completes
    """
    c = account_client
    # create the 3 assets we will use through this test
    assets = build_test_data()
    # add our vuln data
    assets[0].software = build_software()

    # create our temp site
    site = Sites(client=c).create(temp_org.id, site_options=SiteOptions(name="temp-site-for-includes-software-test"))

    # upload our first asset
    sw_task = CustomAssets(client=c).upload_assets(
        temp_org.id,
        site.id,
        temp_custom_integration_with_icon.id,
        assets,
        task_info=ImportTask(name="with-software", exclude_unknown=False),
    )

    # check that the task successfully completed
    status = sw_task.status
    iters = 0
    # keep polling until the task is completed or failed
    # timeout after 300 seconds
    while status not in ("processed", "failed", "error") and iters < __TIMEOUT:
        time.sleep(6)
        iters += 1
        status = Tasks(client=c).get_status(temp_org.id, sw_task.id)
    assert iters != __TIMEOUT  # this is a timeout issue
    assert status == "processed"

    # check out the stats of the first task
    # should be:
    # - 1 new asset
    # - 0 changed assets
    # - 1 asset total
    sw_task = Tasks(client=c).get(temp_org.id, task_id=sw_task.id)
    assert sw_task is not None
    new_assets = sw_task.stats.get("change.newAssets")
    assert new_assets is not None
    assert int(new_assets) == 1
    changed_assets = sw_task.stats.get("change.changedAssets")
    assert changed_assets is not None
    assert int(changed_assets) == 0
    total_assets = sw_task.stats.get("change.totalAssets")
    assert total_assets is not None
    assert int(total_assets) == 1


def build_match_breakable_assets():
    return [
        ImportAsset(
            id="foo1",
            network_interfaces=[
                NetworkInterface(
                    mac_address="01:23:45:67:89:0A",
                    ipv4_addresses=[IPv4Address("192.0.2.1")],
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
                "otherAttribute": "foo",
                "anotherAttribute": "bar",
                "yetAnotherAttr": "baz",
            },
        ),
    ]


@pytest.mark.integration_test
def test_client_end_to_end_with_match_break(account_client, request, tsstring, temp_org, temp_custom_integration):
    ######
    # Setup
    ######

    c = account_client

    site_name = tsstring(f"site for {request.node.name}")
    site_opts = SiteOptions(name=str(site_name))
    created_site = Sites(client=c).create(temp_org.id, site_opts)
    assert created_site.name == site_name

    ######
    # First Batch
    ######

    assets = build_match_breakable_assets()

    created_task = CustomAssets(client=c).upload_assets(
        temp_org.id, created_site.id, temp_custom_integration.id, assets
    )

    status = created_task.status
    iters = 0
    # keep polling until the task is completed or failed, timeout after 300 seconds
    while status not in ("processed", "failed", "error") and iters < __TIMEOUT:
        time.sleep(6)
        iters += 1
        status = Tasks(client=c).get_status(temp_org.id, created_task.id)

    assert iters != __TIMEOUT  # this is a timeout issue
    assert status == "processed"

    # check the task stats to ensure correct processing
    task_info = Tasks(client=c).get(temp_org.id, task_id=created_task.id)
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

    ######
    # Second Batch
    ######

    # change the ID and primary IP and upload the asset again
    assets[0].id = "foo2"
    assets[0].network_interfaces[0].ipv4_addresses = [IPv4Address("192.0.2.2")]

    created_task = CustomAssets(client=c).upload_assets(
        temp_org.id, created_site.id, temp_custom_integration.id, assets
    )

    status = created_task.status
    iters = 0
    # keep polling until the task is completed or failed, timeout after 300 seconds
    while status not in ("processed", "failed", "error") and iters < __TIMEOUT:
        time.sleep(6)
        iters += 1
        status = Tasks(client=c).get_status(temp_org.id, created_task.id)

    assert iters != __TIMEOUT  # this is a timeout issue
    assert status == "processed"

    # check the task stats to ensure correct match break (no updated assets) on foreign ID
    task_info = Tasks(client=c).get(temp_org.id, task_id=created_task.id)
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


@pytest.mark.integration_test
def test_asset_import_include_services(account_client, temp_org, temp_custom_integration_with_icon):
    """
    This test utilizes a temp org/site/integration to ensure idempotency

    1. uploads a single asset with 2 services
    2. asserts that 1 asset was created by checking the task stats after completion successfully completes
    """
    c = account_client
    # create the 3 assets we will use through this test
    assets = build_test_data()
    # add our vuln data
    assets[0].services = build_services()

    # create our temp site
    site = Sites(client=c).create(temp_org.id, site_options=SiteOptions(name="temp-site-for-includes-services-test"))

    # upload our first asset
    svc_task = CustomAssets(client=c).upload_assets(
        temp_org.id,
        site.id,
        temp_custom_integration_with_icon.id,
        assets,
        task_info=ImportTask(name="with-services", exclude_unknown=False),
    )

    # check that the task successfully completed
    status = svc_task.status
    iters = 0
    # keep polling until the task is completed or failed
    # timeout after 300 seconds
    while status not in ("processed", "failed", "error") and iters < __TIMEOUT:
        time.sleep(6)
        iters += 1
        status = Tasks(client=c).get_status(temp_org.id, svc_task.id)
    assert iters != __TIMEOUT  # this is a timeout issue
    assert status == "processed"

    # check out the stats of the first task
    # should be:
    # - 1 new asset
    # - 0 changed assets
    # - 1 asset total
    svc_task = Tasks(client=c).get(temp_org.id, task_id=svc_task.id)
    assert svc_task is not None
    new_assets = svc_task.stats.get("change.newAssets")
    assert new_assets is not None
    assert int(new_assets) == 1
    changed_assets = svc_task.stats.get("change.changedAssets")
    assert changed_assets is not None
    assert int(changed_assets) == 0
    total_assets = svc_task.stats.get("change.totalAssets")
    assert total_assets is not None
    assert int(total_assets) == 1
