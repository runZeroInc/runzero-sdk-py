import time

import pytest

from runzero import CustomAssets, Sites, Tasks, assets_from_csv, assets_from_json
from runzero.admin import CustomSourcesAdmin, OrgsAdmin
from runzero.client import ClientError
from runzero.types import OrgOptions, SiteOptions

from .utils import build_test_data_path


@pytest.mark.integration_test
def test_client_end_to_end_import(account_client, request, tsstring):
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

    csv_path = build_test_data_path("assets.csv")
    assets = assets_from_csv(csv_path)
    assets += assets_from_json(data)

    created_task = CustomAssets(client=c).upload_assets(created_org.id, created_site.id, custom_source.id, assets)

    status = created_task.status
    iters = 0
    # keep polling until the task is completed or failed
    # timeout after 120 seconds
    while status not in ("processed", "failed", "error") and iters < 20:
        time.sleep(6)
        iters += 1
        status = Tasks(client=c).get_status(created_org.id, created_task.id)

    assert status == "processed"

    # teardown Org
    OrgsAdmin(client=c).delete(created_org.id)
    with pytest.raises(ClientError):
        OrgsAdmin(client=c).get(created_org.id)

    # teardown custom source
    CustomSourcesAdmin(client=c).delete(custom_source.id)
    with pytest.raises(ClientError):
        CustomSourcesAdmin(client=c).get(source_id=custom_source.id)
