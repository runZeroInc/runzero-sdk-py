import pytest

from runzero.api import Sites
from runzero.client import ClientError
from runzero.types import SiteOptions


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "client",
    [
        (pytest.lazy_fixture("account_client")),
        (pytest.lazy_fixture("org_client")),
    ],
)
def test_client_site_get(client, integration_config):
    """
    This test demonstrates getting one or more sites
    """
    c = client
    sites = Sites(client=c).get_all(integration_config.org_id)
    assert len(sites) > 0

    site = Sites(client=c).get(integration_config.org_id, site_id=sites[0].id)
    assert site.id == sites[0].id

    site = Sites(client=c).get(integration_config.org_id, name=sites[0].name)
    assert site.id == sites[0].id
    assert site.name == sites[0].name


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "client",
    [
        (pytest.lazy_fixture("account_client")),
        (pytest.lazy_fixture("org_client")),
    ],
)
def test_client_site_create_and_delete(client, integration_config, request, tsstring):
    """
    This test demonstrates creating a site
    """
    c = client
    site_mgr = Sites(client=c)
    site_name = tsstring(f"site for {request.node.name}")
    create_opts = SiteOptions(name=str(site_name))
    created_site = site_mgr.create(integration_config.org_id, site_options=create_opts)
    assert created_site.name == site_name

    site = site_mgr.get(integration_config.org_id, site_id=created_site.id)
    assert site == created_site

    site_mgr.delete(site_id=site.id, org_id=integration_config.org_id)
    with pytest.raises(ClientError):
        site_mgr.get(site_id=site.id, org_id=integration_config.org_id)


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "client",
    [
        (pytest.lazy_fixture("account_client")),
        (pytest.lazy_fixture("org_client")),
    ],
)
def test_client_site_update(client, integration_config, request, temp_site, tsstring):
    """
    This test demonstrates deleting a site
    """
    c = client
    site_mgr = Sites(client=c)
    got_site = site_mgr.get(org_id=integration_config.org_id, site_id=temp_site.id)
    assert got_site.id == temp_site.id
    new_name = tsstring(f"renamed site for {request.node.name}")
    updated_site = site_mgr.update(
        site_id=got_site.id, site_options=SiteOptions(name=str(new_name)), org_id=integration_config.org_id
    )
    assert updated_site.name == new_name
    assert updated_site.id == got_site.id


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "client",
    [
        (pytest.lazy_fixture("account_client")),
        (pytest.lazy_fixture("org_client")),
    ],
)
def test_client_site_create_twice_is_error(client, integration_config, request, tsstring):
    """
    This test demonstrates creating a site with the same name twice is an error
    """
    c = client
    site_mgr = Sites(client=c)
    site_name = tsstring(f"site for {request.node.name}")
    create_opts = SiteOptions(name=str(site_name))
    created_site = site_mgr.create(integration_config.org_id, site_options=create_opts)
    assert created_site.name == site_name

    with pytest.raises(ClientError):
        site_mgr.create(org_id=integration_config.org_id, site_options=create_opts)

    # tear down site from test
    site_mgr.delete(integration_config.org_id, created_site.id)
    with pytest.raises(ClientError):
        site_mgr.get(integration_config.org_id, site_id=created_site.id)
