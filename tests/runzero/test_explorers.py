import pytest

from runzero.api import Explorers
from runzero.client import ClientError
from runzero.types import Explorer

# TODO: Get an explorer specifically reserved for integration tests
# Insert ID into integration test config


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "client",
    [
        (pytest.lazy_fixture("account_client")),
        (pytest.lazy_fixture("org_client")),
    ],
)
def test_client_explorer_get(client, integration_config, explorers, uuid_nil):
    """
    This test demonstrates getting one or more explorers
    """
    c = client
    if not explorers:
        pytest.skip("Explorers cannot be created via API, must skip integration test if none exist")
    assert len(explorers) > 0

    explorer = Explorers(client=c).get(integration_config.org_id, explorer_id=explorers[0].id)
    assert explorer.id == explorers[0].id

    explorer = Explorers(client=c).get(integration_config.org_id, name=explorers[0].name)
    assert explorer.id == explorers[0].id
    assert explorer.id != uuid_nil
    assert explorer.name == explorers[0].name
    assert explorer.name != ""

    with pytest.raises(ClientError) as exc_info:
        explorer = Explorers(client=c).get(integration_config.org_id, explorer_id=uuid_nil)
    assert exc_info.value.error_info is None  # unfortunately, older API
    assert str(exc_info.value) == "The request was rejected by the server: 404: Not Found"

    # Search by name doesn't raise the client error.
    # TODO: Raise ClientError manually here and similar. Potentially create a
    # specific NotFoundError as a sub-type
    explorer = Explorers(client=c).get(integration_config.org_id, name="no explorer with this name")
    assert exc_info.value.error_info is None  # unfortunately, older API
    assert str(exc_info.value) == "The request was rejected by the server: 404: Not Found"


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "client",
    [
        (pytest.lazy_fixture("account_client")),
        (pytest.lazy_fixture("org_client")),
    ],
)
def test_client_explorer_update(client, integration_config, request, tsstring, explorers):
    """
    This test demonstrates updating a explorer
    """
    c = client
    if not explorers:
        pytest.skip("Explorers cannot be created via API, must skip integration test if none exist")
    assert len(explorers) > 0
    assert (
        Explorers(client=c).update_to_latest_version(org_id=integration_config.org_id, explorer_id=explorers[0].id)
        is None
    )


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "client",
    [
        (pytest.lazy_fixture("account_client")),
        (pytest.lazy_fixture("org_client")),
    ],
)
def test_client_explorer_move_to_site(client, integration_config, request, tsstring, temp_site, explorers):
    """
    This test demonstrates moving an explorer to a new site and back
    """
    c = client
    if not explorers:
        pytest.skip("Explorers cannot be created via API, must skip integration test if none exist")
    assert len(explorers) > 0

    explorer = explorers[0]
    old_site_id = explorer.site_id
    moved_explorer = Explorers(client=c).move_to_site(integration_config.org_id, explorer.id, temp_site.id)
    assert moved_explorer.id == explorer.id
    assert moved_explorer.site_id == temp_site.id

    moved_explorer = Explorers(client=c).move_to_site(integration_config.org_id, explorer.id, old_site_id)
    assert moved_explorer.site_id == old_site_id


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "client",
    [
        (pytest.lazy_fixture("account_client")),
        (pytest.lazy_fixture("org_client")),
    ],
)
def test_client_explorer_delete(client, integration_config):
    """
    This test demonstrates moving an explorer to a new site and back
    """
    c = client
    with pytest.raises(ClientError) as exc_info:
        # The explorer's UUID is definitely not the org id
        Explorers(client=c).delete(org_id=integration_config.org_id, explorer_id=integration_config.org_id)
    assert exc_info.value.error_info is None
    assert str(exc_info.value) == "The request was rejected by the server: 404: Not Found"
