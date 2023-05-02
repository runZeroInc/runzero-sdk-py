import pytest

from runzero.api import HostedZones, Scans
from runzero.client import ClientError
from runzero.types import ScanOptions, SiteOptions


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "client",
    [
        (pytest.lazy_fixture("account_client")),
        (pytest.lazy_fixture("org_client")),
    ],
)
def test_client_scan_create(client, integration_config, tsstring, request, temp_site, explorers):
    """
    This test demonstrates creating a scan from scratch, using scan options
    """
    if len(explorers) == 0:
        # No explorers returns a particular error when a scan is created
        pytest.skip("test cannot complete without explorers connected to the server")

    c = client
    scan_mgr = Scans(client=c)
    target = "nonexistenthost8904713251251231.local"
    scan_name = str(tsstring(f"scan for {request.node.name}"))

    # Must set one or more probe names from a list of existing, server-validated choices.
    with pytest.raises(ClientError) as exc_info:
        scan_opts = ScanOptions(probes="nothing", targets=target)
        scan_mgr.create(integration_config.org_id, site_id=temp_site.id, scan_options=scan_opts)
    assert exc_info.value.error_info.status == 400
    assert exc_info.value.error_info.detail == "unknown probe: nothing"

    # can provide site id
    scan_opts = ScanOptions(targets="nonexistenthost8904713251251231.local", probes="arp", scan_name=scan_name)
    try:
        created_task = Scans(client=c).create(
            org_id=integration_config.org_id, site_id=temp_site.id, scan_options=scan_opts
        )
    except ClientError as exc:
        if exc.error_info.detail == "no available agents":
            pytest.skip("cannot run test with no explorers connected, task creation fails")
        raise
    assert created_task.site_id == temp_site.id
    assert created_task.name == scan_name


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "client",
    [
        (pytest.lazy_fixture("account_client")),
        (pytest.lazy_fixture("org_client")),
    ],
)
def test_client_scan_create_from_existing(client, integration_config, tsstring, request, temp_site, explorers):
    """
    This test demonstrates creating a scan from an existing scan/template
    """

    if len(explorers) == 0:
        # No explorers returns a particular error when a scan is created
        pytest.skip("test cannot complete without explorers connected to the server")

    c = client
    scan_mgr = Scans(client=c)
    target = "nonexistenthost8904713251251231.local"
    scan_name = str(tsstring(f"scan for {request.node.name}"))

    # Must set one or more probe names from a list of existing, server-validated choices.
    with pytest.raises(ClientError) as exc_info:
        scan_opts = ScanOptions(probes="nothing", targets=target)
        scan_mgr.create(integration_config.org_id, site_id=temp_site.id, scan_options=scan_opts)
    assert exc_info.value.error_info.status == 400
    assert exc_info.value.error_info.detail == "unknown probe: nothing"

    scan_opts = ScanOptions(targets="nonexistenthost8904713251251231.local", probes="arp", scan_name=scan_name)
    try:
        created_task = scan_mgr.create(integration_config.org_id, site_id=temp_site.id, scan_options=scan_opts)
    except ClientError as exc:
        if exc.error_info.detail == "no available agents":
            pytest.skip("cannot run test with no explorers connected, task creation fails")
        raise
    assert created_task.name == scan_name


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "client",
    [
        (pytest.lazy_fixture("account_client")),
        (pytest.lazy_fixture("org_client")),
    ],
)
def test_client_scan_create_with_hosted_zone_id(
    client, integration_config, tsstring, request, temp_site, uuid_nil, hosted_zones, explorers
):
    """
    This test demonstrates creating a scan using a hosted zone id
    """

    if len(hosted_zones) == 0:
        pytest.skip("cannot run test with no hosted zones accessible")

    if len(explorers) == 0:
        pytest.skip("test cannot complete without explorers connected")

    c = client
    conf = integration_config
    hosted_zone = hosted_zones[0]
    scan_mgr = Scans(client=c)
    target = "nonexistenthost8904713251251231.local"
    scan_name = str(tsstring(f"scan for {request.node.name}"))

    scan_opts = ScanOptions(
        targets="nonexistenthost8904713251251231.local",
        probes="arp",
        scan_name=scan_name,
        hosted_zone_id=str(hosted_zone.id),
    )
    created_task = scan_mgr.create(integration_config.org_id, site_id=temp_site.id, scan_options=scan_opts)
    assert created_task.name == scan_name
    assert created_task.hosted_zone_id == hosted_zone.id

    scan_opts = ScanOptions(
        targets="nonexistenthost8904713251251231.local", probes="arp", scan_name=scan_name, hosted_zone_name="auto"
    )

    try:
        created_task = scan_mgr.create(integration_config.org_id, site_id=temp_site.id, scan_options=scan_opts)
    except ClientError as exc:
        if exc.error_info.detail == "no available agents":
            pytest.skip("cannot run test with no explorers connected, task creation fails")
        raise

    assert created_task.name == scan_name
    assert created_task.hosted_zone_id != uuid_nil
