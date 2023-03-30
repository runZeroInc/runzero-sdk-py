import pytest

from runzero.api import OrgsAdmin
from runzero.client import AuthError, ClientError
from runzero.types import OrgOptions


@pytest.mark.integration_test
def test_client_orgs_requires_account_key(org_client):
    with pytest.raises(AuthError):
        OrgsAdmin(client=org_client).get_all()


@pytest.mark.integration_test
def test_client_orgs_get(account_client):
    """
    This test demonstrates getting one or more orgs
    """
    c = account_client
    orgs = OrgsAdmin(client=c).get_all()
    assert len(orgs) > 0

    org = OrgsAdmin(client=c).get(org_id=orgs[0].id)
    assert org.id == orgs[0].id

    org = OrgsAdmin(client=c).get(name=orgs[0].name)
    assert org.id == orgs[0].id
    assert org.name == orgs[0].name


@pytest.mark.integration_test
def test_client_org_create_and_delete(account_client, integration_config, request, tsstring):
    """
    This test demonstrates creating an org
    """
    c = account_client
    org_mgr = OrgsAdmin(client=c)
    org_name = tsstring(f"org for {request.node.name}")
    create_opts = OrgOptions(name=str(org_name))
    created_org = org_mgr.create(org_options=create_opts)
    assert created_org.name == org_name

    org = org_mgr.get(org_id=created_org.id)
    assert org == created_org

    org_mgr.delete(org_id=org.id)
    with pytest.raises(ClientError):
        org_mgr.get(org_id=created_org.id)


@pytest.mark.integration_test
def test_client_org_update(account_client, integration_config, request, temp_org, tsstring):
    """
    This test demonstrates deleting an org
    """
    c = account_client
    org_mgr = OrgsAdmin(client=c)
    got_org = org_mgr.get(org_id=temp_org.id)
    assert got_org.id == temp_org.id
    new_name = tsstring(f"renamed org for {request.node.name}")
    updated_org = org_mgr.update(org_id=got_org.id, org_options=OrgOptions(name=str(new_name)))
    assert updated_org.name == new_name
    assert updated_org.id == got_org.id


@pytest.mark.integration_test
def test_client_org_create_twice_is_error(account_client, integration_config, request, tsstring):
    """
    This test demonstrates creating an org with the same name twice is an error
    """
    c = account_client
    org_mgr = OrgsAdmin(client=c)
    org_name = tsstring(f"org for {request.node.name}")
    create_opts = OrgOptions(name=str(org_name))
    created_org = org_mgr.create(org_options=create_opts)
    assert created_org.name == org_name

    with pytest.raises(ClientError):
        org_mgr.create(org_options=create_opts)

    # teardown org from test
    org_mgr.delete(created_org.id)
    with pytest.raises(ClientError):
        org_mgr.get(org_id=created_org.id)
