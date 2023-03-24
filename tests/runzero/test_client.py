import pytest

from runzero.admin import OrgsAdmin
from runzero.client import Client
from runzero.client.errors import ConnError


def test_client_init_and_defaults():
    """
    This test demonstrates getting one or more sites
    """
    c = Client()
    assert c.server_url == "https://console.runzero.com"
    assert c.timeout == 30

    with pytest.raises(ValueError):
        Client(timeout_seconds=0)

    with pytest.raises(ValueError):
        Client(timeout_seconds=-1)

    with pytest.raises(ValueError):
        Client(server_url="http://insecure.local")


@pytest.mark.integration_test
def test_client_connection_server_missing(integration_config):
    """
    This test ensures we can use the client id and secret to retrieve a valid OAuth token and use that OAuth token
    for both account and organization scope APIs
    """
    with pytest.raises(ConnError):
        c = Client(
            account_key=integration_config.account_token,
            server_url="https://its.not.there.local:8888",
            timeout_seconds=1,
        )
        OrgsAdmin(client=c).get_all()
