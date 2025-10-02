import pytest

from runzero.api import OrgsAdmin
from runzero.client import AuthError, ClientError
from runzero.types import OrgOptions


@pytest.mark.integration_test
def test_client_orgs_requires_account_key(org_client):
    with pytest.raises(AuthError):
        OrgsAdmin(client=org_client).get_all()


@pytest.mark.integration_test
def test_client_orgs_get(account_client, temp_org):
    """
    This test demonstrates getting one or more orgs
    """
    c = account_client
    orgs = OrgsAdmin(client=c).get_all()
    assert len(orgs) > 0

    org = OrgsAdmin(client=c).get(org_id=temp_org.id)
    assert org.id == temp_org.id

    org = OrgsAdmin(client=c).get(name=temp_org.name)
    assert org.id == temp_org.id
    assert org.name == temp_org.name


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
    if (
        equal_ignore_fields(
            org,
            created_org,
            [
                "export_token",
                "export_token_created_at",
                "export_token_last_used_at",
                "export_token_last_used_by",
                "export_token_counter",
            ],
        )
        != True
    ):
        # asserting here instead of equal_ignore_fields gives better error messages
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


def equal_ignore_fields(obj1, obj2, ignore_fields=None):
    if ignore_fields is None:
        ignore_fields = []

    if type(obj1) != type(obj2):
        return False

    for field in obj1.__dict__:  # Assuming objects have __dict__ for attributes
        if field in ignore_fields:
            continue
        value1 = getattr(obj1, field)
        value2 = getattr(obj2, field)

        # For other fields or if the special condition wasn't met
        if value1 != value2:
            return False
    return True
