import uuid

import pytest

from runzero.api import HostedZones


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "client",
    [
        (pytest.lazy_fixture("account_client")),
        (pytest.lazy_fixture("org_client")),
    ],
)
def test_hosted_zones_get(client, integration_config):
    c = client
    conf = integration_config
    hosted_zones = HostedZones(client=c).get_all(conf.org_id)
    if not hosted_zones:
        pytest.skip("Hosted zones cannot be created via API, must skip integration test if none exist")
    assert len(hosted_zones) > 0

    # requires either name or id
    with pytest.raises(ValueError):
        HostedZones(client=c).get(integration_config.org_id)

    hosted_zone = HostedZones(client=c).get(integration_config.org_id, name=hosted_zones[0].name)
    assert hosted_zone.name == hosted_zones[0].name
    assert hosted_zone.name != ""
    assert hosted_zone.id == hosted_zones[0].id
    assert hosted_zone.id != uuid.UUID("00000000-0000-0000-0000-000000000000")

    hosted_zone = HostedZones(client=c).get(integration_config.org_id, hosted_zone_id=hosted_zones[0].id)
    assert hosted_zone.name == hosted_zones[0].name
    assert hosted_zone.id == hosted_zones[0].id
